from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Sequence
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Optional
from uuid import uuid4

from .models import DatasetDetail, DatasetMetadata, DatasetStatus


class DatasetStore:
    """A thread-safe, SQLite-backed store for dataset metadata and content."""

    def __init__(self, db_path: str = "data/ingestor.db") -> None:
        self.db_path = db_path
        self._lock = Lock()
        
        # Ensure the data directory exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Initializes the SQLite tables if they do not exist."""
        with self._lock:
            with self._get_connection() as conn:
                # Add status and error_message columns (with defaults for migration)
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS datasets (
                        id TEXT PRIMARY KEY,
                        file_name TEXT NOT NULL,
                        upload_time TEXT NOT NULL,
                        record_count INTEGER NOT NULL,
                        status TEXT NOT NULL DEFAULT 'completed',
                        error_message TEXT,
                        columns TEXT,
                        records TEXT
                    )
                """)
                conn.commit()

    def create_pending(self, file_name: str) -> DatasetMetadata:
        """
        Creates a new dataset entry in the 'processing' state.
        Allocates the ID so it can be tracked by the frontend before parsing is done.
        """
        dataset_id = str(uuid4())
        upload_time = datetime.now(timezone.utc).isoformat()
        
        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO datasets (id, file_name, upload_time, record_count, status) VALUES (?, ?, ?, ?, ?)",
                    (dataset_id, file_name, upload_time, 0, DatasetStatus.PROCESSING.value),
                )
                conn.commit()

        return DatasetMetadata(
            id=dataset_id,
            file_name=file_name,
            upload_time=datetime.fromisoformat(upload_time),
            record_count=0,
            status=DatasetStatus.PROCESSING,
        )

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
        records_json = json.dumps(list(records)) if records else "[]"
        columns_json = json.dumps(columns) if columns else "[]"
        record_count = len(records)

        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    "UPDATE datasets SET record_count = ?, columns = ?, records = ?, status = ?, error_message = ? WHERE id = ?",
                    (record_count, columns_json, records_json, status.value, error_message, dataset_id),
                )
                conn.commit()
                return cursor.rowcount > 0

    def list(self) -> list[DatasetMetadata]:
        """Returns all datasets sorted by upload time (newest first)."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT id, file_name, upload_time, record_count, status, error_message FROM datasets ORDER BY upload_time DESC")
                rows = cursor.fetchall()

        return [
            DatasetMetadata(
                id=row["id"],
                file_name=row["file_name"],
                upload_time=datetime.fromisoformat(row["upload_time"]),
                record_count=row["record_count"],
                status=DatasetStatus(row["status"]),
                error_message=row["error_message"],
            )
            for row in rows
        ]

    def get(self, dataset_id: str) -> DatasetDetail | None:
        """
        Fetches detailed information for a specific dataset from SQLite.
        """
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM datasets WHERE id = ?", (dataset_id,))
                row = cursor.fetchone()

        if not row:
            return None

        # Handle columns/records being potentially NULL for processing datasets
        columns = json.loads(row["columns"]) if row["columns"] else []
        all_records = json.loads(row["records"]) if row["records"] else []
        preview = all_records[:20]

        metadata = DatasetMetadata(
            id=row["id"],
            file_name=row["file_name"],
            upload_time=datetime.fromisoformat(row["upload_time"]),
            record_count=row["record_count"],
            status=DatasetStatus(row["status"]),
            error_message=row["error_message"],
        )
        return DatasetDetail(metadata=metadata, columns=columns, preview=preview)

    def delete(self, dataset_id: str) -> bool:
        """Removes a dataset from the SQLite database."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
                conn.commit()
                return cursor.rowcount > 0
