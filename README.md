# 🚀 Data Ingestion System

A robust, real-time **All-in-One Dashboard** designed for seamless dataset management. Upload, validate, and preview CSV and JSON data in a unified, professional workspace with live synchronization.

---

## ✨ Key Features

-   **Unified Workspace**: List, search, and detailed data previews are all visible on a single page for maximum efficiency.
-   **Professional UI**: Clean, high-contrast design focused on data readability and intuitive navigation.
-   **Modal Upload Workflow**: Ingest new data without losing your current view via a non-blocking overlay.
-   **Real-Time Synchronization**: Uses WebSockets to sync dataset lists and deletions across all connected clients instantly.
-   **Smart JSON Support**: Accepts both standard arrays of objects and single objects (automatically wrapped).
-   **Premium UX**: Featuring smooth transitions, progress emulation, and a non-blocking "Toast" notification system.
-   **State Persistence**: Remembers your workspace (selection, search, sort) using browser `localStorage`.

---

## 🛠️ Technology Stack

### Backend
-   **FastAPI**: High-performance Python web framework.
-   **Uvicorn**: ASGI server for handling WebSockets and HTTP.
-   **Pydantic**: Data validation and settings management.
-   **Custom Resilient Parser**: Built-in logic for robust CSV/JSON sanitization.

### Frontend
-   **React + Vite**: Fast, modern frontend development.
-   **Vanilla CSS**: Premium, custom-crafted styles with a focus on aesthetics.
-   **WebSockets**: Real-time server-sent events.

## 🛡️ Production Hardening & Security

This system is built with following enterprise-grade security features:

- **Data Persistence**: Uses a **SQLite Database** (`data/ingestor.db`) with Docker Volumes to ensure data survives restarts.
- **Resource Protection**: Implemented a **50MB Backend Safeguard** to prevent RAM exhaustion (OOM) attacks.
- **Rate Limiting**: Enforces API rate limits (e.g., 5 uploads/min) using **SlowAPI** to prevent brute-force abuse.
- **Non-Root Runtime**: Both Backend and Frontend containers run as a non-privileged **`appuser`** for container isolation.
- **Automated Monitoring**: Includes Docker **HEALTHCHECK** instructions for both services.

---

## 🚢 Docker Deployment (Recommended)

The easiest way to run the entire stack is using **Docker Compose**.

### 1. Build and Run
```bash
docker-compose up --build
```

---

## 🚦 Getting Started

### Prerequisites
-   Python 3.10+
-   Node.js 18+

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*The backend will run on `http://localhost:8000`.*

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
*The frontend will run on `http://localhost:5173`.*

---

## 🔌 API Reference

### Datasets
-   `GET /datasets`: List all uploaded datasets.
-   `POST /upload`: Upload a new CSV or JSON file.
-   `GET /datasets/{id}`: Get metadata and records preview for a dataset.
-   `DELETE /datasets/{id}`: Remove a dataset.

### Real-Time
-   `WS /ws`: WebSocket endpoint for event notifications (`dataset_uploaded`, `dataset_deleted`).

---

## 🛡️ Validation & Reliability
-   **Thread-Safety**: The in-memory store uses `threading.Lock` for concurrent safely.
-   **Global Error Handling**: A centralized exception handler ensures all unexpected errors return a clean JSON response.
-   **Sanitization**: All incoming data is cleaned (header stripping, null-to-empty string conversion) before storage.

---

## 📝 License
MIT
