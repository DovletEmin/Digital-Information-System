# Production-ready Dockerfile for SMU Digital Library
# Compatible with Python 3.10.12
FROM python:3.10-slim as base

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

# Copy requirements file
COPY requirements.txt /app/requirements.txt

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

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

# Expose port
EXPOSE 8000

# Default command
CMD ["gunicorn", "src.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
