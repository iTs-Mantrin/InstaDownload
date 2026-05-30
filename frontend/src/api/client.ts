// Set VITE_API_URL to your BACKEND ROOT URL (e.g. https://backend.railway.app)
// Do NOT include /api suffix — it's added automatically.
// Falls back to `/api` for local dev proxy or single-service setup.
const BACKEND_URL: string = (import.meta.env.VITE_API_URL || '').replace(/\/+$/, '')
const API_BASE: string = BACKEND_URL ? `${BACKEND_URL}/api` : '/api'

export interface ProgressState {
  percent: number
  speed: string
  eta: string
  filename: string
  status: string
  error_msg: string
  download_url?: string | null
}

export interface DownloadResponse {
  task_id: string
  source: string
}

export interface FormatInfo {
  format_id: string
  height: number | null
  ext: string
  filesize: number | null
  vcodec: string
  acodec: string
  tbr: number | null
}

export interface PreviewInfo {
  title: string
  duration: number
  uploader: string
  webpage_url: string
  thumbnail: string
  formats: FormatInfo[]
}

// ── Route helper ──────────────────────────────────────────────
// Backend routes are per-source: /api/youtube/download, /api/instagram/preview, etc.
function apiFor(source: string, endpoint: string): string {
  return `${API_BASE}/${source}/${endpoint}`
}

export async function startDownload(params: {
  url: string
  source: string
  quality?: string
  audio_only?: boolean
}): Promise<DownloadResponse> {
  const res = await fetch(apiFor(params.source, 'download'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: params.url, quality: params.quality, audio_only: params.audio_only }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Download request failed')
  }
  return res.json()
}

export async function getProgress(taskId: string, source: string): Promise<ProgressState> {
  const res = await fetch(apiFor(source, `progress/${taskId}`))
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Progress fetch failed')
  }
  return res.json()
}

export function getDownloadUrl(taskId: string, source: string): string {
  return apiFor(source, `file/${taskId}`)
}

export function resolveApiUrl(path: string): string {
  if (/^https?:\/\//i.test(path)) return path
  if (BACKEND_URL) {
    return `${BACKEND_URL}${path.startsWith('/') ? path : `/${path}`}`
  }
  return path
}

export async function cancelTask(taskId: string, source: string): Promise<void> {
  await fetch(apiFor(source, taskId), { method: 'DELETE' })
}

export async function previewUrl(url: string, source: string): Promise<PreviewInfo> {
  const res = await fetch(apiFor(source, 'preview'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Preview fetch failed')
  }
  return res.json()
}

export async function fetchInstagramStories(username: string): Promise<DownloadResponse> {
  const res = await fetch(`${API_BASE}/instagram/stories?username=${encodeURIComponent(username)}`, {
    method: 'POST',
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Stories fetch failed')
  }
  return res.json()
}

export function getProfilePicUrl(username: string): string {
  return `${API_BASE}/instagram/profile-pic/${encodeURIComponent(username)}`
}

// ── Instagram User Feed ───────────────────────────────────────

export interface UserMediaItem {
  id: string
  url: string
  title: string
  thumbnail: string
  duration: number | null
  source: 'profile' | 'story'
}

export interface UserFeedResponse {
  username: string
  media: UserMediaItem[]
  media_count: number
}

export async function fetchInstagramUserFeed(username: string): Promise<UserFeedResponse> {
  const res = await fetch(`${API_BASE}/instagram/user-feed`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Failed to fetch user feed')
  }
  return res.json()
}
