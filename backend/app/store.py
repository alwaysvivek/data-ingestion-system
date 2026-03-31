from __future__ import annotations

import json
import os
import sqlite3
from collections.abc import Sequence
from datetime import datetime, timezone
from threading import Lock
from typing import Any
from uuid import uuid4

from .models import DatasetDetail, DatasetMetadata


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
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS datasets (
                        id TEXT PRIMARY KEY,
                        file_name TEXT NOT NULL,
                        upload_time TEXT NOT NULL,
                        record_count INTEGER NOT NULL,
                        columns TEXT NOT NULL,
                        records TEXT NOT NULL
                    )
                """)
                conn.commit()

    def create(self, file_name: str, records: Sequence[dict[str, Any]], columns: list[str]) -> DatasetMetadata:
        """
        Creates a new dataset entry and stores it in the SQLite database.
        """
        dataset_id = str(uuid4())
        upload_time = datetime.now(timezone.utc).isoformat()
        record_count = len(records)
        
        # Serialize records and columns for storage
        records_json = json.dumps(list(records))
        columns_json = json.dumps(columns)

        with self._lock:
            with self._get_connection() as conn:
                conn.execute(
                    "INSERT INTO datasets (id, file_name, upload_time, record_count, columns, records) VALUES (?, ?, ?, ?, ?, ?)",
                    (dataset_id, file_name, upload_time, record_count, columns_json, records_json),
                )
                conn.commit()

        return DatasetMetadata(
            id=dataset_id,
            file_name=file_name,
            upload_time=datetime.fromisoformat(upload_time),
            record_count=record_count,
        )

    def list(self) -> list[DatasetMetadata]:
        """Returns all datasets sorted by upload time (newest first)."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT id, file_name, upload_time, record_count FROM datasets ORDER BY upload_time DESC")
                rows = cursor.fetchall()

        return [
            DatasetMetadata(
                id=row["id"],
                file_name=row["file_name"],
                upload_time=datetime.fromisoformat(row["upload_time"]),
                record_count=row["record_count"],
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

        # Deserialize columns and records
        columns = json.loads(row["columns"])
        all_records = json.loads(row["records"])
        preview = all_records[:20]

        metadata = DatasetMetadata(
            id=row["id"],
            file_name=row["file_name"],
            upload_time=datetime.fromisoformat(row["upload_time"]),
            record_count=row["record_count"],
        )
        return DatasetDetail(metadata=metadata, columns=columns, preview=preview)

    def delete(self, dataset_id: str) -> bool:
        """Removes a dataset from the SQLite database."""
        with self._lock:
            with self._get_connection() as conn:
                cursor = conn.execute("DELETE FROM datasets WHERE id = ?", (dataset_id,))
                conn.commit()
                return cursor.rowcount > 0
