from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DetectionBase(BaseModel):
    label: str = "building"
    latitude: float
    longitude: float
    address: Optional[str] = None
    confidence: float = 0.0
    bbox_left: Optional[float] = None
    bbox_top: Optional[float] = None
    bbox_width: Optional[float] = None
    bbox_height: Optional[float] = None


class DetectionRead(DetectionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
