from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..db.base import Base
from .enums import ImageStatus


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(100), nullable=False)
    storage_path = Column(String(500), nullable=False)
    status = Column(Enum(ImageStatus), default=ImageStatus.new, nullable=False)
    source = Column(String(100), default="uploaded", nullable=False)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    query_id = Column(Integer, ForeignKey("queries.id"), nullable=True)

    project = relationship("Project", back_populates="images")
    query = relationship("Query", back_populates="images")
    detections = relationship("Detection", back_populates="image", cascade="all, delete-orphan")
