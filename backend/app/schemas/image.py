from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ..models.enums import ImageStatus
from .detection import DetectionRead


class ImageBase(BaseModel):
    id: int
    filename: str
    content_type: str
    status: ImageStatus
    source: str
    uploaded_at: datetime
    processed_at: Optional[datetime]
    project_id: Optional[int]
    query_id: Optional[int]

    class Config:
        orm_mode = True


class ImageWithDetections(ImageBase):
    detections: List[DetectionRead] = []
