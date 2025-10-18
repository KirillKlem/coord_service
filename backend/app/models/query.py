from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from ..db.base import Base
from .enums import QueryStatus, QueryType


class Query(Base):
    __tablename__ = "queries"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(Enum(QueryType), nullable=False, default=QueryType.predict)
    status = Column(Enum(QueryStatus), nullable=False, default=QueryStatus.pending)
    params = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    result_count = Column(Integer, default=0, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)

    user = relationship("User", back_populates="queries")
    project = relationship("Project", back_populates="queries")
    images = relationship("Image", back_populates="query")
