# Krishika AI — Production Dockerfile
# Python 3.11 matches .python-version and is compatible with tensorflow-cpu 2.10-2.16

# ── Stage 1: Builder ──────────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# ── Stage 2: Production ───────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm

WORKDIR /app

# Install runtime libs for OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app /app

EXPOSE 8001

# Production defaults — override all sensitive values via docker run -e or docker-compose env_file
ENV PYTHONUNBUFFERED=1
ENV DEBUG=false
ENV PORT=8001
ENV WARMUP_ON_START=true
ENV UPLOAD_DIR=uploads
ENV APP_VERSION=1.0.0

# MONGO_URI, MONGO_DB_NAME, JWT_SECRET_KEY, CORS_ORIGINS must be injected at runtime.
# DO NOT hardcode credentials here.

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
