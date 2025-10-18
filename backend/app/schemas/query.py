from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..models.enums import QueryStatus, QueryType


class QueryRead(BaseModel):
    id: int
    type: QueryType
    status: QueryStatus
    params: Optional[Dict[str, Any]]
    created_at: datetime
    completed_at: Optional[datetime]
    result_count: int

    class Config:
        orm_mode = True
