FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps (if any packages need compilation) and curl for health checks
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
# If a local 'wheelhouse' directory exists in the project, copy it into the image
# and install from it (air-gapped build). Otherwise fall back to normal pip install.
COPY wheelhouse /wheelhouse
# If a local wheelhouse exists, use it as an additional find-links source
# but allow pip to fall back to PyPI for packages not present in the wheelhouse.
RUN if [ -d /wheelhouse ] && [ "$(ls -A /wheelhouse)" ]; then \
    echo "Using local wheelhouse for offline install"; \
    pip install --no-cache-dir --no-index --find-links /wheelhouse -r /app/requirements.txt; \
    else \
    echo "No wheelhouse found — installing from PyPI"; \
    pip install --no-cache-dir -r /app/requirements.txt; \
    fi

# Copy project (still mountable by compose for active development)
COPY . /app

# Default command for worker; compose will override for beat if needed
CMD ["celery", "-A", "src", "worker", "--loglevel=info"]
