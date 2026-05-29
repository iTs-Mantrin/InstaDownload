# ---- Build frontend ----
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ---- Backend ----
FROM python:3.12-slim

WORKDIR /app

# Install ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY backend/ .

# Copy built frontend
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Default env (PORT is overridden by Railway's $PORT at runtime)
ENV HOST=0.0.0.0
ENV PORT=8000
ENV DOWNLOAD_DIR=/tmp/instadownload

EXPOSE $PORT

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
