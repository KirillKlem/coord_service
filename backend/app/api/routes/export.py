from io import BytesIO
from zipfile import ZipFile

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from ...models import Image, Query, User
from ...services.storage import storage_service
from .. import deps

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/xlsx")
def export_xlsx(
    query_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = db.query(Query).filter(Query.id == query_id, Query.user_id == current_user.id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    images = db.query(Image).filter(Image.query_id == query_id).all()

    wb = Workbook()
    ws = wb.active
    ws.title = "Detections"
    ws.append(
        [
            "Image ID",
            "Filename",
            "Latitude",
            "Longitude",
            "Address",
            "Confidence",
            "BBox Left",
            "BBox Top",
            "BBox Width",
            "BBox Height",
        ]
    )
    for image in images:
        for detection in image.detections:
            ws.append(
                [
                    image.id,
                    image.filename,
                    detection.latitude,
                    detection.longitude,
                    detection.address,
                    detection.confidence,
                    detection.bbox_left,
                    detection.bbox_top,
                    detection.bbox_width,
                    detection.bbox_height,
                ]
            )
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    filename = f"georag_query_{query_id}.xlsx"
    headers = {"Content-Disposition": f"attachment; filename={filename}"}
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers=headers,
    )


@router.get("/images")
def export_images(
    query_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
):
    query = db.query(Query).filter(Query.id == query_id, Query.user_id == current_user.id).first()
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    images = db.query(Image).filter(Image.query_id == query_id).all()

    buffer = BytesIO()
    with ZipFile(buffer, "w") as zip_file:
        for image in images:
            try:
                path = storage_service.open_file(image.storage_path)
                zip_file.write(path, arcname=image.filename)
            except FileNotFoundError:
                continue
    buffer.seek(0)
    headers = {"Content-Disposition": f"attachment; filename=georag_query_{query_id}.zip"}
    return StreamingResponse(buffer, media_type="application/zip", headers=headers)
