from __future__ import annotations

from datetime import datetime
from typing import Iterable, List

from sqlalchemy.orm import Session

from ..db.session import SessionLocal
from ..models import Detection, Image, Query
from ..models.enums import ImageStatus, QueryStatus
from .geocoder import geocoder
from .predictor import Predictor
from .storage import storage_service
from .metrics import FAILED_PREDICTIONS, PREDICTION_COUNTER


predictor = Predictor()


def process_images(db: Session, query: Query, images: Iterable[Image]) -> None:
    query.status = QueryStatus.running
    db.add(query)
    db.commit()
    db.refresh(query)

    total_detections = 0
    try:
        for image in images:
            try:
                image.status = ImageStatus.processing
                db.add(image)
                db.commit()
                db.refresh(image)

                image_path = storage_service.open_file(image.storage_path)
                predictions = predictor.predict(image_path)
                detections: List[Detection] = []
                for pred in predictions:
                    address = geocoder.reverse(pred.latitude, pred.longitude)
                    detection = Detection(
                        image_id=image.id,
                        label=pred.label,
                        latitude=pred.latitude,
                        longitude=pred.longitude,
                        address=address,
                        confidence=pred.confidence,
                        bbox_left=pred.bbox_left,
                        bbox_top=pred.bbox_top,
                        bbox_width=pred.bbox_width,
                        bbox_height=pred.bbox_height,
                    )
                    detections.append(detection)
                for detection in detections:
                    db.add(detection)
                image.status = ImageStatus.processed
                image.processed_at = datetime.utcnow()
                total_detections += len(detections)
                db.add(image)
                db.commit()
            except Exception:  # noqa: B902
                FAILED_PREDICTIONS.inc()
                image.status = ImageStatus.failed
                db.add(image)
                db.commit()
    finally:
        query.status = QueryStatus.completed
        query.completed_at = datetime.utcnow()
        query.result_count = total_detections
        db.add(query)
        db.commit()
        PREDICTION_COUNTER.inc()


def process_images_background(image_ids: List[int], query_id: int) -> None:
    db: Session = SessionLocal()
    try:
        query = db.query(Query).filter(Query.id == query_id).first()
        if not query:
            return
        images = db.query(Image).filter(Image.id.in_(image_ids)).all()
        process_images(db, query, images)
    finally:
        db.close()
