# Multi-stage build for production optimization
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements/ /app/requirements/

# Install Python dependencies based on environment
ARG ENV=prod
RUN if [ "$ENV" = "prod" ]; then \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements/prod.txt; \
    else \
    pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements/dev.txt; \
    fi

# Copy application code
COPY --chown=appuser:appuser . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/src/staticfiles /app/src/media && \
    chown -R appuser:appuser /app/logs /app/src/staticfiles /app/src/media && \
    chmod -R 755 /app/logs /app/src/staticfiles /app/src/media

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/home/appuser/.local/bin:$PATH"

# Switch to non-root user
USER appuser

# Default command
CMD ["gunicorn", "src.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
