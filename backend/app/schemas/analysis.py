from typing import List, Optional

from pydantic import BaseModel

from ..models.enums import QueryStatus
from .image import ImageWithDetections
from .query import QueryRead


class PredictResult(BaseModel):
    query: QueryRead
    images: List[ImageWithDetections]


class PredictResponse(BaseModel):
    query_id: int
    status: QueryStatus
    images: Optional[List[ImageWithDetections]] = None


class SearchResponse(BaseModel):
    query: QueryRead
    results: List[ImageWithDetections]
