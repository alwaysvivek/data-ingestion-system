# 🚀 Data Ingestion System (Unified Monolith)

A professional, real-time **All-in-One Dashboard** designed for seamless dataset management. This system allows users to upload, validate, and preview CSV and JSON data in a unified workspace with live synchronization and persistent PostgreSQL storage.

---

## ✅ Task 1 Requirements Coverage

This implementation fulfills all requirements for **Task 1: Data Ingestion Module**:

### Backend
- **POST /upload**: Accepts CSV/JSON, validates schema, and stores in PostgreSQL (`JSONB`).
- **GET /datasets**: Returns a sorted list of all uploaded dataset metadata.
- **GET /datasets/{id}**: Fetches metadata and a high-performance record preview.
- **Validation**: Strict schema consistency checks and resilient parsing for `None` values.

### Frontend
- **File Upload**: Modal-based with **Drag & Drop** support.
- **Listing & Search**: Sidebar library with real-time status updates via WebSockets.
- **Detail View**: Interactive **Pro Table** with inferred data types and metadata display.
- **UX**: Professional status messages (Toast) and progress indicators.

---

## ✨ Key Features

- **Unified Architecture**: Frontend and Backend are bundled into a single high-performance service for simplified hosting and zero CORS issues.
- **PostgreSQL Persistence**: Powered by **SQLAlchemy ORM** and **PostgreSQL (Neon DB)**, featuring native **JSONB** storage.
- **Resilient Parsing**: Automatically cleans CSV headers and handles missing/null values gracefully (converted to empty strings or native `null`).
- **Schema Validation**: Rejects files with inconsistent columns to ensure data integrity.
- **Real-Time Sync**: Instant UI updates across all clients using **WebSockets**.

---

## 🛡️ Validation & Reliability

- **Null Handling**: Missing CSV cells are converted to `""`. JSON `null` values are preserved and rendered as `null` badges in the UI.
- **Schema Integrity**: The first row defines the "source of truth." Any row with missing/extra fields triggers a `400 Bad Request`.
- **Large File Support**: Enforced **50MB limit** to prevent OOM errors.
- **Rate Limiting**: Rate limits on `/upload` and `/datasets` to prevent abuse.

---

## 🛠️ Technology Stack

| Layer | Technologies |
|---|---|
| **Backend** | FastAPI, SQLAlchemy, PostgreSQL (Neon), Pydantic, SlowAPI |
| **Frontend** | React, Vite, Vanilla CSS |
| **DevOps** | Docker (Multi-stage), Render Blueprints, GitHub Actions |

---

## 🚦 Local Development

### 1. Prerequisites
- Python 3.11+
- Node.js 18+
- A PostgreSQL instance (e.g., [Neon.tech](https://neon.tech))

### 2. Setup
```bash
# 1. Clone & Setup Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure Environment
# Create 'backend/.env' with:
# DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

# 3. Start Servers
uvicorn app.main:app --reload  # Backend at port 8000
cd ../frontend && npm install && npm run dev  # Frontend at port 5173
```

---

## 🚢 Deployment

### Docker (Unified Build)
Build and run the entire system as a single containerized monolith:
```bash
docker build -t data-ingestion-system .
docker run -p 8000:8000 -e DATABASE_URL="your_db_url" data-ingestion-system
```

### Render Blueprint
1. Go to **Render Dashboard** -> **New** -> **Blueprint**.
2. Connect this repository.
3. Set the `DATABASE_URL` environment variable.

---

## 🔌 API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/datasets` | List all uploaded datasets. |
| `POST` | `/upload` | Upload CSV/JSON (Multipart form). |
| `GET` | `/datasets/{id}`| Fetch metadata and preview records. |
| `DELETE`| `/datasets/{id}`| Remove dataset and records. |
| `WS` | `/ws` | Real-time event notifications. |

---

## 📝 License
MIT
