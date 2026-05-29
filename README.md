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

Railway auto-detects the `Dockerfile` and `railway.json` in this repo. The app includes all config-as-code for a smooth deployment.

### Step-by-step

1. **Push the repo to GitHub** if you haven't already.

2. **Go to [Railway](https://railway.app) → New Project → Deploy from GitHub repo.** Select your repository.

3. Railway auto-detects the `Dockerfile` and builds the app. No additional build commands needed.

4. **Add a PostgreSQL database:**
   - In your Railway project dashboard, click **Add a Database** → **PostgreSQL**.
   - Railway automatically injects the `DATABASE_URL` into your app's environment.

5. **Add Redis (optional — required for queue features):**
   - Click **Add a Database** → **Redis**.
   - Railway injects the `REDIS_URL` into your app's environment.

6. **Set required environment variables** in the Variables tab:
   - `SECRET_KEY` — generate a random string (`openssl rand -hex 32`)
   - `DOWNLOAD_DIR` — set to `/tmp/instadownload` (default)

7. **Generate a public domain:**
   - Go to the **Networking** tab → **Generate Domain**.
   - Your app is live at `https://your-app.railway.app`.

### Health checks

The app exposes `/api/health` which Railway uses to verify the deployment is ready. Configured in `railway.json`.

### GitHub deploy (zero-downtime)

Every push to your default branch triggers an automatic deployment. Railway performs rolling updates — zero downtime.

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
