from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query as QueryParam,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session

from ...core.config import settings
from ...models import Detection, Image, Project, Query, User
from ...models.enums import ImageStatus, QueryStatus, QueryType
from ...schemas import PredictResponse, QueryRead, SearchResponse
from ...services.geocoder import geocoder
from ...services.metrics import CURRENT_TASKS, UPLOAD_COUNTER
from ...services.storage import storage_service
from ...services.tasks import process_images, process_images_background
from ...utils.geo import bounding_box, haversine_distance_km
from .. import deps

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _ensure_project(db: Session, project_id: Optional[int], user: User) -> Optional[Project]:
    if project_id is None:
        return None
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/predict", response_model=PredictResponse, status_code=status.HTTP_202_ACCEPTED)
def predict(
    background_tasks: BackgroundTasks,
    project_id: Optional[int] = Form(default=None),
    files: List[UploadFile] = File(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No files provided")
    project = _ensure_project(db, project_id, current_user)
    query = Query(
        type=QueryType.predict,
        status=QueryStatus.pending,
        params={"file_count": len(files)},
        user_id=current_user.id,
        project_id=project.id if project else None,
    )
    db.add(query)
    db.commit()
    db.refresh(query)

    images: List[Image] = []
    for file in files:
        destination = storage_service.save_file(file)
        image = Image(
            filename=file.filename or destination.name,
            content_type=file.content_type or "application/octet-stream",
            storage_path=storage_service.get_public_path(destination),
            status=ImageStatus.new,
            project_id=project.id if project else None,
            query_id=query.id,
        )
        db.add(image)
        images.append(image)
        UPLOAD_COUNTER.inc()
    db.commit()
    for image in images:
        db.refresh(image)

    if len(images) <= settings.sync_max_images:
        CURRENT_TASKS.inc()
        try:
            process_images(db, query, images)
        finally:
            CURRENT_TASKS.dec()
        refreshed_query = db.query(Query).filter(Query.id == query.id).first()
        refreshed_images = db.query(Image).filter(Image.query_id == query.id).all()
        return PredictResponse(
            query_id=refreshed_query.id,
            status=refreshed_query.status,
            images=[image_to_schema(image) for image in refreshed_images],
        )
    else:
        image_ids = [image.id for image in images]
        CURRENT_TASKS.inc()
        background_tasks.add_task(_background_task_wrapper, image_ids, query.id)
        return PredictResponse(query_id=query.id, status=QueryStatus.running)


def image_to_schema(image: Image):
    _ = list(image.detections)
    return image


def _background_task_wrapper(image_ids: List[int], query_id: int) -> None:
    try:
        process_images_background(image_ids, query_id)
    finally:
        CURRENT_TASKS.dec()


@router.get("/predict/{query_id}", response_model=PredictResponse)
def get_predict_result(
    query_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = db.query(Query).filter(Query.id == query_id, Query.user_id == current_user.id).first()
    if not query:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Query not found")
    images = db.query(Image).filter(Image.query_id == query_id).all()
    return PredictResponse(
        query_id=query.id,
        status=query.status,
        images=[image_to_schema(image) for image in images] if query.status == QueryStatus.completed else None,
    )


@router.get("/search", response_model=SearchResponse)
def search(
    project_id: Optional[int] = None,
    address: Optional[str] = None,
    lat: Optional[float] = QueryParam(default=None, ge=-90, le=90),
    lon: Optional[float] = QueryParam(default=None, ge=-180, le=180),
    radius_km: float = QueryParam(default=0.5, gt=0.0, le=10.0),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    if not address and (lat is None or lon is None):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Specify address or coordinates")
    _ensure_project(db, project_id, current_user)

    if address:
        geo = geocoder.forward(address)
        lat, lon = geo.latitude, geo.longitude

    min_lat, max_lat, min_lon, max_lon = bounding_box(lat, lon, radius_km)
    detections_query = db.query(Detection).join(Image).filter(
        Detection.latitude >= min_lat,
        Detection.latitude <= max_lat,
        Detection.longitude >= min_lon,
        Detection.longitude <= max_lon,
    )
    if project_id:
        detections_query = detections_query.filter(Image.project_id == project_id)
    detections = detections_query.all()

    result_images: dict[int, Image] = {}
    for detection in detections:
        if haversine_distance_km(lat, lon, detection.latitude, detection.longitude) <= radius_km:
            result_images.setdefault(detection.image_id, detection.image)
    images = list(result_images.values())

    query_entry = Query(
        type=QueryType.search,
        status=QueryStatus.completed,
        params={"lat": lat, "lon": lon, "radius": radius_km, "address": address},
        user_id=current_user.id,
        project_id=project_id,
        created_at=datetime.utcnow(),
        completed_at=datetime.utcnow(),
        result_count=len(images),
    )
    db.add(query_entry)
    db.commit()
    db.refresh(query_entry)

    return SearchResponse(
        query=QueryRead.from_orm(query_entry),
        results=[image_to_schema(image) for image in images],
    )
