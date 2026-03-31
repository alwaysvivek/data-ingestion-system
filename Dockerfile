# Stage 1: Build the React Frontend
FROM node:20-alpine as frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the Final Monolithic Service
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create a non-privileged user for security
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories and set ownership
RUN mkdir -p data static && chown -R appuser:appgroup /app

# Copy the Backend application code
COPY ./backend/app ./app

# Copy the Frontend build artifacts from Stage 1 into the 'static' folder
COPY --from=frontend-builder /app/frontend/dist ./static
RUN chown -R appuser:appgroup /app/static

# Final ownership check
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the API and UI (Unified on Port 8000)
EXPOSE 8000

# Healthcheck for automated monitoring
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI application (serving both API and Static UI)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
