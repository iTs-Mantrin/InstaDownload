# ── Stage 1: Build frontend ──────────────────────────────
FROM node:20-slim AS frontend-builder

WORKDIR /build

# Install dependencies (cached separately)
COPY frontend/package*.json ./
RUN npm ci

# Copy and build
COPY frontend/ .
RUN npm run build

# ── Stage 2: Python backend ──────────────────────────────
FROM python:3.12-slim

WORKDIR /app

# Install ffmpeg for video merging
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /build/dist frontend/dist

# Use PORT from Railway env
ENV HOST=0.0.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8000}/api/health')"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
