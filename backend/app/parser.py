import csv
import io
import json
from typing import Any

from fastapi import HTTPException


def parse_and_validate(file_name: str, content: bytes) -> tuple[list[dict[str, Any]], list[str]]:
    """
    Main entry point for parsing and validating uploaded files.
    Supports CSV and JSON formats.

    Args:
        file_name: Name of the file (used to determine format).
        content: Raw binary content of the file.

    Returns:
        A tuple containing (list of records, list of column names).
    """
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    file_name_lower = file_name.lower()
    if file_name_lower.endswith(".csv"):
        records = _parse_csv(content)
    elif file_name_lower.endswith(".json"):
        records = _parse_json(content)
    else:
        raise HTTPException(status_code=400, detail="Only CSV and JSON files are supported.")

    _validate_records(records)
    schema = list(records[0].keys())
    return records, schema


def _parse_csv(content: bytes) -> list[dict[str, Any]]:
    """
    Parses CSV content with a multi-pass approach for resilience.
    1. Decodes and reads the first line to sanitize headers.
    2. Re-reads with DictReader, using sanitized headers and handling missing/extra row values.
    """
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as error:
        raise HTTPException(status_code=400, detail="CSV file must be UTF-8 encoded.") from error

    try:
        f = io.StringIO(text)
        # Pass 1: Get raw header row and clean it
        base_reader = csv.reader(f)
        try:
            raw_fieldnames = next(base_reader)
        except StopIteration:
            raise HTTPException(status_code=400, detail="CSV file is empty.")

        # Clean header: strip whitespace and ignore empty column names (often from trailing commas)
        cleaned_fieldnames = [name.strip() for name in raw_fieldnames if name and str(name).strip()]

        if not cleaned_fieldnames:
            raise HTTPException(status_code=400, detail="CSV file is missing a valid header row.")

        # Pass 2: Re-parse the whole file using the cleaned headers
        f.seek(0)
        next(f)  # Skip the original header line
        dict_reader = csv.DictReader(f, fieldnames=cleaned_fieldnames, restval="")

        records = []
        for row in dict_reader:
            # Cleanup row:
            # - Ensure all keys are strings
            # - Convert None values to empty strings
            # - Ignore values from columns that weren't in our cleaned header (k is not None)
            clean_row = {str(k): (v if v is not None else "") for k, v in row.items() if k is not None}
            records.append(clean_row)

    except (csv.Error, UnicodeDecodeError) as error:
        raise HTTPException(status_code=400, detail=f"Failed to parse CSV: {error}") from error

    if not records:
        raise HTTPException(status_code=400, detail="CSV file does not contain any data rows.")
    return records


def _parse_json(content: bytes) -> list[dict[str, Any]]:
    """
    Parses JSON content with support for both single objects and arrays of objects.
    """
    try:
        parsed = json.loads(content.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise HTTPException(status_code=400, detail="Failed to parse JSON file.") from error

    # Resilience: Automatically wrap a single object into a list if it's not already an array
    if isinstance(parsed, dict):
        parsed = [parsed]

    if not isinstance(parsed, list) or not parsed:
        raise HTTPException(
            status_code=400,
            detail="JSON file must contain a non-empty array of objects or a single valid object.",
        )
    if not all(isinstance(item, dict) for item in parsed):
        raise HTTPException(status_code=400, detail="Each JSON record must be an object (dictionary).")
    return parsed


def _validate_records(records: list[dict[str, Any]]) -> None:
    """
    Ensures structural integrity of the dataset.
    All records must contain the same set of keys (schema consistency).
    """
    if not records:
        return

    base_keys = set(records[0].keys())
    if not base_keys:
        raise HTTPException(status_code=400, detail="Dataset records must contain at least one field.")

    for index, record in enumerate(records, start=1):
        keys = set(record.keys())
        if keys != base_keys:
            raise HTTPException(
                status_code=400,
                detail=f"Inconsistent schema at row {index}. Expected keys: {sorted(base_keys)}.",
            )
