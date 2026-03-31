import logging
import os
import time

from fastapi import FastAPI, File, HTTPException, Request, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .logging_config import configure_logging
from .models import DatasetDetail, DatasetMetadata
from .parser import parse_and_validate
from .realtime import ConnectionManager
from .store import DatasetStore

# 1. Initialize Global Services
configure_logging()
logger = logging.getLogger("data-ingestion")

# Rate Limiter Configuration
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Data Ingestion System")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Database Store (Uses SQLite in production-grade data/ directory)
store = DatasetStore(db_path=os.getenv("DATABASE_URL", "data/ingestor.db"))
connections = ConnectionManager()

# 2. Hardened Middleware Configuration

# Dynamic CORS based on environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_safeguards(request: Request, call_next):
    """
    Middleware to enforce production security limits:
    - Max Request Size: 50MB (Prevents RAM exhaustion/OOM DoS)
    """
    # 50MB Limit
    MAX_FILE_SIZE = 50 * 1024 * 1024
    
    if request.method == "POST" and request.url.path == "/upload":
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_FILE_SIZE:
            return JSONResponse(
                status_code=413,
                content={"detail": "File too large. Maximum allowed size is 50MB."}
            )

    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    
    # Log completions
    logger.info(
        "request.completed",
        extra={
            "extra": {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            }
        },
    )
    return response

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global catch-all for unhandled exceptions."""
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An internal server error occurred. Please try again later."},
    )

@app.get("/health")
def health() -> dict[str, str]:
    """Health check endpoint for Docker/Kubernetes monitoring."""
    return {"status": "ok"}

@app.post("/upload", response_model=DatasetMetadata)
@limiter.limit("5/minute")
async def upload_dataset(request: Request, file: UploadFile = File(...)) -> DatasetMetadata:
    """
    Accepts CSV or JSON file, parses it, validates schema, and stores it in SQLite.
    Includes a 5-per-minute rate limit for this endpoint.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="File name is missing.")

    content = await file.read()
    
    records, columns = parse_and_validate(file.filename, content)
    dataset = store.create(file.filename, records, columns)
    
    logger.info(
        "dataset.uploaded",
        extra={
            "extra": {
                "dataset_id": dataset.id,
                "file_name": dataset.file_name,
                "record_count": dataset.record_count,
            }
        },
    )
    
    await connections.broadcast({"event": "dataset_uploaded", "dataset_id": dataset.id})
    return dataset

@app.get("/datasets", response_model=list[DatasetMetadata])
@limiter.limit("60/minute")
def list_datasets(request: Request) -> list[DatasetMetadata]:
    """Lists metadata for all uploaded datasets."""
    return store.list()

@app.delete("/datasets/{dataset_id}")
@limiter.limit("10/minute")
async def delete_dataset(request: Request, dataset_id: str) -> dict[str, str]:
    """Deletes a dataset by ID."""
    success = store.delete(dataset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Dataset not found.")

    logger.info("dataset.deleted", extra={"extra": {"dataset_id": dataset_id}})
    await connections.broadcast({"event": "dataset_deleted", "dataset_id": dataset_id})
    return {"status": "ok"}

@app.get("/datasets/{dataset_id}", response_model=DatasetDetail)
@limiter.limit("30/minute")
def get_dataset(request: Request, dataset_id: str) -> DatasetDetail:
    """Fetches details (metadata + preview) for a single dataset."""
    dataset = store.get(dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found.")
    return dataset

# 3. Static File Serving (Unified Container)
# Serves the React 'dist' directory from the root path
# Only if the 'static' directory exists (built by monolithic Docker)
frontend_path = os.path.join(os.getcwd(), "static")
if os.path.exists(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="static")

@app.websocket("/ws")
async def websocket_updates(websocket: WebSocket):
    """WebSocket endpoint for real-time updates."""
    await connections.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.disconnect(websocket)
