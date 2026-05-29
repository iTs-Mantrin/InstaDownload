const API_BASE = '/api'

export interface ProgressState {
  percent: number
  speed: string
  eta: string
  filename: string
  status: string
  error_msg: string
}

export interface DownloadResponse {
  task_id: string
  source: string
}

export interface PreviewInfo {
  title: string
  duration: number
  uploader: string
  webpage_url: string
  thumbnail: string
}

export async function startDownload(params: {
  url: string
  source: string
  quality?: string
  audio_only?: boolean
}): Promise<DownloadResponse> {
  const res = await fetch(`${API_BASE}/download`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || 'Download request failed')
  }
  return res.json()
}

export async function getProgress(taskId: string): Promise<ProgressState> {
  const res = await fetch(`${API_BASE}/progress/${taskId}`)
  if (!res.ok) throw new Error('Progress fetch failed')
  return res.json()
}

export function getDownloadUrl(taskId: string): string {
  return `${API_BASE}/file/${taskId}`
}

export async function cancelTask(taskId: string): Promise<void> {
  await fetch(`${API_BASE}/cancel/${taskId}`, { method: 'DELETE' })
}

export async function previewUrl(url: string, source: string): Promise<PreviewInfo> {
  const res = await fetch(`${API_BASE}/preview`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, source }),
  })
  if (!res.ok) throw new Error('Preview fetch failed')
  return res.json()
}

export async function fetchInstagramStories(username: string): Promise<string[]> {
  const res = await fetch(`${API_BASE}/instagram/stories?username=${encodeURIComponent(username)}`, {
    method: 'POST',
  })
  if (!res.ok) throw new Error('Stories fetch failed')
  return res.json()
}

export function getProfilePicUrl(username: string): string {
  return `${API_BASE}/instagram/profile-pic/${encodeURIComponent(username)}`
}
