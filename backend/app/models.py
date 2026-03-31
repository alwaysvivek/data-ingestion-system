from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel


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


class DatasetDetail(BaseModel):
    metadata: DatasetMetadata
    columns: list[str]
    preview: list[dict[str, Any]]
