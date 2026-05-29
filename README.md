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
- **Ad-ready** — ad unit placeholders on every page

## Quick Start (local)

### Prerequisites

- Python 3.12+
- Node.js 20+
- ffmpeg (for YouTube merging)

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API at `http://localhost:8000`.

### Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Dev server at `http://localhost:5173` — proxies `/api` to the backend.

### Production build (single-service)

```bash
cd frontend
npm run build
```

Then start the backend — it serves the built frontend automatically.

---

## Deploy to Railway (two services)

The app is split into **two Railway services**:

| Service | Type | Root dir | Port |
|---|---|---|---|
| **Backend** | Docker service | `backend/` | 8000 |
| **Frontend** | Static Site | `frontend/` | 443 |

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USER/instadownload.git
git push -u origin main
```

### 2. Create Backend Service

1. Go to [Railway dashboard](https://railway.app) → **New Project** → **Deploy from GitHub repo**
2. Select your repo
3. Railway auto-detects `railway.json` and builds from `backend/Dockerfile`
4. Wait for the build to finish (first deploy will fail — expected, env vars missing)

### 3. Add Environment Variables (Backend)

In **Variables** tab, set:

| Variable | Value |
|---|---|
| `SECRET_KEY` | `openssl rand -hex 32` (run this command) |
| `PORT` | `8000` |
| `CORS_ORIGINS` | `*` (or lock to your frontend URL later) |
| `DOWNLOAD_DIR` | `/tmp/instadownload` |

Optional but recommended — click **Add a Database** → **PostgreSQL** and **Redis**. Railway auto-injects `DATABASE_URL` and `REDIS_URL`.

### 4. Generate Backend Domain

1. Go to **Networking** tab → **Generate Domain**
2. Copy the URL — you'll need it for the frontend build
3. Example: `https://backend-production-1234.up.railway.app`

### 5. Create Frontend Service

1. In the same Railway project, click **New** → **Static Site**
2. Select the same GitHub repo
3. Configure:

| Setting | Value |
|---|---|
| **Root Directory** | `frontend` |
| **Build Command** | `npm install && npm run build` |
| **Publish Directory** | `dist` |

4. Add a **build variable** (NOT a regular variable):

| Variable | Value |
|---|---|
| **VITE_API_URL** | `https://your-backend.railway.app` (from step 4) |

5. Click **Deploy**

### 6. Generate Frontend Domain

Go to the frontend service **Networking** tab → **Generate Domain**.

Your app is live at `https://frontend-production-xxxx.up.railway.app`.

### 7. Verify it works

Visit your frontend URL. Paste a YouTube URL and try downloading.

Check the backend health:
```
https://your-backend.railway.app/api/health
```

Should return: `{"status": "ok", "app": "InstaDownload", ...}`

---

## Docker (backend only, local)

```bash
cd backend
docker build -t instadownload-backend .
docker run -p 8000:8000 instadownload-backend
```

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
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `YT_DLP_COOKIES_FILE` | — | Path to Netscape-format cookies file |

### Frontend build-time env

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Backend URL (required for two-service Railway setup) |

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy (async), PostgreSQL, Redis, yt-dlp
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS 4
- **Deployment**: Docker, Railway

## License

MIT
