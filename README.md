# 🚀 Data Ingestion System (Unified Monolith)

A robust, real-time **All-in-One Dashboard** designed for seamless dataset management. Upload, validate, and preview CSV and JSON data in a unified, professional workspace with live synchronization and persistent PostgreSQL storage.

---

## ✨ Key Features

-   **Unified Monolith Architecture**: Frontend and Backend are bundled into a single high-performance service for simplified hosting and zero CORS issues.
-   **PostgreSQL Persistence**: Powered by **SQLAlchemy ORM** and **PostgreSQL (Neon DB)**, featuring native **JSONB** storage for schema-less record efficiency.
-   **Smart Schema Validation**: Automatically ensures data consistency across rows and validates file formats (CSV/JSON).
-   **Real-Time Synchronization**: Uses WebSockets to sync dataset states across all connected clients instantly.
-   **Pro Table Preview**: Inferred data types (Number, Date, Boolean, Text) and interactive previews for uploaded data.
-   **State Persistence**: Remembers your workspace (selection, search, sort) using browser `localStorage`.

---

## 🛠️ Technology Stack

### Backend
-   **FastAPI**: High-performance Python web framework.
-   **SQLAlchemy**: Advanced ORM for robust database interactions.
-   **PostgreSQL (Neon)**: Cloud-native database with JSONB support.
-   **Uvicorn**: ASGI server for handling WebSockets and HTTP.

### Frontend
-   **React + Vite**: Fast, modern frontend development.
-   **Vanilla CSS**: Premium, custom-crafted styles with a focus on aesthetics.
-   **WebSockets**: Real-time server-sent events for live UI updates.

---

## 🛡️ Production Hardening & Security

- **Unified Container**: Both Frontend and Backend run in a single multi-stage Docker container.
- **Resource Protection**: 50MB Backend Safeguard to prevent RAM exhaustion (OOM) attacks.
- **Rate Limiting**: Enforces API rate limits (e.g., 5 uploads/min) using **SlowAPI**.
- **Non-Root Runtime**: Containers run as a non-privileged **`appuser`** for maximum isolation.
- **Automated Monitoring**: Includes Docker **HEALTHCHECK** instructions for service reliability.

---

## 🚢 Docker Deployment (Recommended)

The entire stack can be deployed as a single service using the multi-stage Dockerfile.

### 1. Build and Run
```bash
docker build -t data-ingestion-system .
docker run -p 8000:8000 -e DATABASE_URL="your_neon_url" data-ingestion-system
```

### 2. Render One-Click (Blueprint)
This project includes a `render.yaml` for instant deployment. 
1. Connect your repo to Render.
2. Select **New -> Blueprint**.
3. Provide your `DATABASE_URL`.

---

## 🚦 Local Development

### Prerequisites
-   Python 3.11+
-   Node.js 18+
-   A PostgreSQL database (or Neon DB connection string)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
# Create a .env file with DATABASE_URL
uvicorn app.main:app --reload
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 🔌 API Reference

### Datasets
-   `GET /datasets`: List all uploaded datasets metadata.
-   `POST /upload`: Upload a new CSV or JSON file.
-   `GET /datasets/{id}`: Get metadata and records preview.
-   `DELETE /datasets/{id}`: Remove a dataset.

### Real-Time
-   `WS /ws`: WebSocket endpoint for event notifications (`dataset_uploaded`, `dataset_deleted`).

---

## 📝 License
MIT
