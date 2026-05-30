# YouTube Downloader Backend

Stateless YouTube downloader backend built with FastAPI, yt-dlp, and FFmpeg.

## Stack

- FastAPI
- yt-dlp
- FFmpeg
- No database
- No Redis
- No background worker

## Project structure

```text
backend/
├── main.py
├── routes/
├── services/
├── utils/
├── requirements.txt
├── Dockerfile
└── .env.example
```

## Features

- `POST /api/info` for title, thumbnail, duration, and format options
- `POST /api/download` for MP4 or MP3 download link generation
- Signed temporary download URLs
- Automatic temp file cleanup
- CORS support for React frontends
- `.env` support
- Docker-ready for Render, Railway, and VPS deployment

## Requirements

- Python 3.12+
- FFmpeg installed locally for non-Docker runs

## Local setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API base URL: `http://localhost:8000/api`

Health check: `http://localhost:8000/health`

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `APP_NAME` | `YouTube Downloader API` | FastAPI app name |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |
| `DEBUG` | `false` | Debug mode |
| `CORS_ORIGINS` | `*` | Comma-separated frontend origins |
| `TEMP_DIR` | `/tmp/youtube-downloader` | Temporary download directory |
| `DOWNLOAD_TOKEN_SECRET` | `change-me-in-production` | Secret used to sign download links |
| `DOWNLOAD_TOKEN_TTL_SECONDS` | `900` | Download link lifetime |
| `YT_DLP_COOKIES_FILE` | empty | Optional cookies file for restricted access cases |

## API

### `POST /api/info`

Request body:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

Example response:

```json
{
  "title": "Example video",
  "thumbnail": "https://...jpg",
  "duration": 213,
  "formats": [
    {
      "format": "mp4",
      "quality": "highest",
      "label": "Best quality MP4",
      "extension": "mp4",
      "filesize": null
    },
    {
      "format": "mp3",
      "quality": "192",
      "label": "192 kbps MP3",
      "extension": "mp3",
      "filesize": null
    }
  ]
}
```

### `POST /api/download`

Request body for MP4:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp4",
  "quality": "720"
}
```

Request body for MP3:

```json
{
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "format": "mp3",
  "quality": "192"
}
```

Response:

```json
{
  "download_url": "http://localhost:8000/api/downloads/<token>",
  "filename": "Example video-dQw4w9WgXcQ.mp3",
  "format": "mp3",
  "quality": "192",
  "expires_in": 900,
  "extension": "mp3"
}
```

## Example curl requests

```bash
curl -X POST http://localhost:8000/api/info \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}'
```

```bash
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","format":"mp4","quality":"highest"}'
```

```bash
curl -X POST http://localhost:8000/api/download \
  -H "Content-Type: application/json" \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ","format":"mp3","quality":"192"}'
```

## Error handling

The API returns clear HTTP errors for:

- Invalid URL
- Private video
- Age-restricted video
- Unavailable video
- Download failure

## Docker

```bash
cd backend
docker build -t youtube-downloader-api .
docker run --env-file .env -p 8000:8000 youtube-downloader-api
```

## Deployment notes

### Render

- Use `backend/` as the root directory
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add `DOWNLOAD_TOKEN_SECRET` and `CORS_ORIGINS`

### Railway

- Use `backend/` as the service root
- Deploy with the included Dockerfile
- Set `PORT`, `DOWNLOAD_TOKEN_SECRET`, and `CORS_ORIGINS`
- Railway ephemeral storage is fine because downloads are temporary

### VPS

- Install Python and FFmpeg
- Copy `.env.example` to `.env`
- Run with Uvicorn directly or behind Nginx
- Use systemd or Docker for process supervision

## Frontend integration

Your React frontend can call:

- `POST /api/info`
- `POST /api/download`

Then redirect the browser to the returned `download_url`.
