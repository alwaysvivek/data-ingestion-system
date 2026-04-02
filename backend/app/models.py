from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, JSON
from sqlalchemy.dialects.postgresql import JSONB

from .database import Base


class DatasetStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DatasetMetadata(BaseModel):
    id: str
    file_name: str
    upload_time: datetime
    record_count: int
    status: DatasetStatus = DatasetStatus.COMPLETED
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class DatasetDetail(BaseModel):
    metadata: DatasetMetadata
    columns: list[str]
    preview: list[dict[str, Any]]


class DatasetORM(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, index=True)
    file_name = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    record_count = Column(Integer, default=0, nullable=False)
    status = Column(String, default=DatasetStatus.PROCESSING.value, nullable=False)
    error_message = Column(String, nullable=True)
    # Using JSONB for PostgreSQL efficiency
    columns = Column(JSONB, nullable=True)
    records = Column(JSONB, nullable=True)
