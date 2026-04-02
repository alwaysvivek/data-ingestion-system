from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import DatasetDetail, DatasetMetadata, DatasetORM, DatasetStatus


class DatasetStore:
    """A thread-safe, SQLAlchemy-backed store for dataset metadata and content."""

    def __init__(self, session_factory=SessionLocal) -> None:
        self.SessionLocal = session_factory

    def create_pending(self, file_name: str) -> DatasetMetadata:
        """
        Creates a new dataset entry in the 'processing' state.
        Allocates the ID so it can be tracked by the frontend before parsing is done.
        """
        dataset_id = str(uuid4())
        upload_time = datetime.now(timezone.utc)
        
        with self.SessionLocal() as session:
            new_dataset = DatasetORM(
                id=dataset_id,
                file_name=file_name,
                upload_time=upload_time,
                record_count=0,
                status=DatasetStatus.PROCESSING.value
            )
            session.add(new_dataset)
            session.commit()
            session.refresh(new_dataset)

            return DatasetMetadata.from_orm(new_dataset)

    def update_completion(
        self, 
        dataset_id: str, 
        records: Sequence[dict[str, Any]], 
        columns: list[str],
        status: DatasetStatus = DatasetStatus.COMPLETED,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Updates a pending dataset with its parsed data and final status.
        Uses a transaction for atomic update of all fields.
        """
        with self.SessionLocal() as session:
            dataset = session.query(DatasetORM).filter(DatasetORM.id == dataset_id).first()
            if not dataset:
                return False
            
            dataset.record_count = len(records) if records else 0
            dataset.columns = columns if columns else []
            dataset.records = list(records) if records else []
            dataset.status = status.value
            dataset.error_message = error_message
            
            session.commit()
            return True

    def list(self) -> list[DatasetMetadata]:
        """Returns all datasets sorted by upload time (newest first)."""
        with self.SessionLocal() as session:
            datasets = session.query(DatasetORM).order_by(DatasetORM.upload_time.desc()).all()
            return [DatasetMetadata.from_orm(d) for d in datasets]

    def get(self, dataset_id: str) -> DatasetDetail | None:
        """
        Fetches detailed information for a specific dataset from PostgreSQL.
        """
        with self.SessionLocal() as session:
            dataset = session.query(DatasetORM).filter(DatasetORM.id == dataset_id).first()
            
            if not dataset:
                return None

            metadata = DatasetMetadata.from_orm(dataset)
            columns = dataset.columns or []
            all_records = dataset.records or []
            preview = all_records[:20]

            return DatasetDetail(metadata=metadata, columns=columns, preview=preview)

    def delete(self, dataset_id: str) -> bool:
        """Removes a dataset from the database."""
        with self.SessionLocal() as session:
            dataset = session.query(DatasetORM).filter(DatasetORM.id == dataset_id).first()
            if not dataset:
                return False
            
            session.delete(dataset)
            session.commit()
            return True
