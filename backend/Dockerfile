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

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory for SQLite and set ownership
RUN mkdir -p data && chown appuser:appgroup data

# Copy the application code
COPY ./app ./app
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose the API port
EXPOSE 8000

# Healthcheck for automated monitoring
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
