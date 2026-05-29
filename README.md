# InstaDownload

Download videos and audio from **YouTube** and **Instagram** — fast, free, and private.

- Web app built with **FastAPI** + **React** (Vite + Tailwind)
- Powered by [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- No account required

## Features

- **YouTube**: Download videos up to 4K, extract MP3 audio
- **Instagram**: Download posts, reels, stories, profile pictures
- **Dark / Light mode**
- **Mobile responsive**
- **Paste URL auto-detection** — paste any link and the app navigates to the right tool

## Quick Start (local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- ffmpeg (for YouTube merging)

### Backend

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.

### Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Frontend dev server starts at `http://localhost:5173` with API proxy to `:8000`.

### Production build

```bash
cd frontend
npm run build
```

Then start the backend — it serves the built frontend automatically.

## Docker

```bash
# Build and run with PostgreSQL + Redis
docker compose up --build
```

Or just the app without a database:

```bash
docker build -t instadownload .
docker run -p 8000:8000 -e DATABASE_URL= sqlite:///./data.db instadownload
```

## Deploy to Railway

1. Push to a GitHub repository
2. Connect the repo on [Railway](https://railway.app)
3. The `Procfile` and `Dockerfile` are included for auto-detection
4. Set environment variables:
   - `SECRET_KEY` — a random secret string
   - `DATABASE_URL` — your PostgreSQL connection string (Railway provides this)
   - `REDIS_URL` — your Redis connection string (optional)
   - `DOWNLOAD_DIR` — path for temporary download files (default: `/tmp/instadownload`)

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `HOST` | `0.0.0.0` | Server bind address |
| `PORT` | `8000` | Server port |
| `DEBUG` | `false` | Enable debug mode / hot reload |
| `SECRET_KEY` | `change-me-in-production` | App secret key |
| `DATABASE_URL` | `postgresql+asyncpg://...` | PostgreSQL connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection string |
| `DOWNLOAD_DIR` | `/tmp/instadownload` | Temp download directory |
| `MAX_FILE_AGE_MINUTES` | `30` | Auto-cleanup age for downloads |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Allowed CORS origins |
| `YT_DLP_COOKIES_FILE` | — | Path to Netscape-format cookies file |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL, Redis, yt-dlp
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS 4
- **Deployment**: Docker, Railway-ready

## License

MIT
