from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DatasetMetadata(BaseModel):
    id: str
    file_name: str
    upload_time: datetime
    record_count: int


class DatasetDetail(BaseModel):
    metadata: DatasetMetadata
    columns: list[str]
    preview: list[dict[str, Any]]
