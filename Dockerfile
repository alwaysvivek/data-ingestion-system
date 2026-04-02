# --- Phase 1: Build the Frontend ---
FROM node:18-alpine AS frontend-builder
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# --- Phase 2: Create the Backend Runtime ---
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (needed for psycopg2 and curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/app ./app

# Copy built frontend assets into the 'static' directory
COPY --from=frontend-builder /build/dist ./static

# Set security context
RUN groupadd -r appgroup && useradd -r -g appgroup appuser
RUN chown -R appuser:appgroup /app
USER appuser

# Expose the port (FastAPI default or Render $PORT)
EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start the application
# We use $(pwd) to ensure it finds the 'static' folder correctly
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
