import { useState, useRef, useCallback, useEffect, useMemo } from 'react'
import { startDownload, getProgress, getDownloadUrl, cancelTask, previewUrl, resolveApiUrl } from '../api/client.ts'
import type { ProgressState, PreviewInfo, FormatInfo } from '../api/client.ts'
import ProgressBar from './ProgressBar.tsx'

interface YouTubeDownloaderProps {
  initialUrl?: string
  className?: string
}

/** Extract YouTube video ID from various URL formats. */
function getYoutubeVideoId(url: string): string | null {
  const patterns = [
    /(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/embed\/([a-zA-Z0-9_-]{11})/,
    /youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})/,
  ]
  for (const p of patterns) {
    const m = url.match(p)
    if (m) return m[1]
  }
  return null
}

/** Format bytes to human-readable string. */
function formatSize(bytes: number | null): string {
  if (bytes === null || bytes === undefined) return ''
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

/** Deduplicate formats by height: pick best (prefer mp4, then highest tbr). */
function dedupeFormats(formats: FormatInfo[]): FormatInfo[] {
  const byHeight = new Map<number, FormatInfo[]>()
  for (const f of formats) {
    if (!f.height) continue
    if (f.vcodec === 'none') continue // audio-only
    const arr = byHeight.get(f.height) || []
    arr.push(f)
    byHeight.set(f.height, arr)
  }
  const result: FormatInfo[] = []
  for (const [, group] of byHeight) {
    // Prefer mp4, then larger tbr
    group.sort((a, b) => {
      const aScore = a.ext === 'mp4' ? 1 : 0
      const bScore = b.ext === 'mp4' ? 1 : 0
      if (aScore !== bScore) return bScore - aScore
      return (b.tbr ?? 0) - (a.tbr ?? 0)
    })
    result.push(group[0])
  }
  result.sort((a, b) => (b.height ?? 0) - (a.height ?? 0))
  return result
}

export default function YouTubeDownloader({ initialUrl = '', className = '' }: YouTubeDownloaderProps) {
  const [url, setUrl] = useState(initialUrl)
  const [progress, setProgress] = useState<ProgressState | null>(null)
  const [preview, setPreview] = useState<PreviewInfo | null>(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [previewError, setPreviewError] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [taskId, setTaskId] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const videoId = useMemo(() => preview ? getYoutubeVideoId(preview.webpage_url) : null, [preview])
  const videoFormats = useMemo(() => preview ? dedupeFormats(preview.formats) : [], [preview])

  // ── Auto-preview on URL change (debounced 600ms) ──
  useEffect(() => {
    if (!url.trim()) {
      setPreview(null)
      setPreviewError('')
      return
    }

    const timer = setTimeout(async () => {
      setPreviewLoading(true)
      setPreviewError('')
      try {
        const info = await previewUrl(url.trim(), 'youtube')
        setPreview(info)
      } catch (err) {
        setPreview(null)
        setPreviewError(err instanceof Error ? err.message : 'Could not fetch preview')
      } finally {
        setPreviewLoading(false)
      }
    }, 600)

    return () => clearTimeout(timer)
  }, [url])

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  const handleDownload = async (quality: string) => {
    if (!url.trim()) { setError('Please enter a URL'); return }
    setError('')
    setProgress(null)
    setTaskId(null)
    stopPolling()

    try {
      setLoading(true)
      const { task_id } = await startDownload({
        url: url.trim(),
        source: 'youtube',
        quality,
        audio_only: false,
      })
      setTaskId(task_id)
      setLoading(false)

      pollingRef.current = setInterval(async () => {
        try {
          const p = await getProgress(task_id, 'youtube')
          setProgress(p)
          if (p.status === 'done' || p.status === 'error' || p.status === 'cancelled') {
            if (p.status === 'error' || p.status === 'cancelled') {
              setError(p.error_msg || `Download ${p.status}`)
            }
            stopPolling()
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Progress fetch failed')
          stopPolling()
        }
      }, 500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Download failed')
      setLoading(false)
    }
  }

  const handleCancel = async () => {
    if (taskId) {
      await cancelTask(taskId, 'youtube')
      stopPolling()
    }
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* URL Input */}
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">Video URL</label>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          placeholder="https://youtube.com/watch?v=... or https://youtu.be/..."
          className="w-full px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors"
        />
      </div>

      {/* Loading indicator */}
      {previewLoading && (
        <div className="rounded-xl p-4 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 transition-colors">
          <p className="text-sm text-slate-400 animate-pulse">Fetching video info...</p>
        </div>
      )}

      {previewError && !preview && (
        <p className="text-amber-500 dark:text-amber-400 text-sm">{previewError}</p>
      )}

      {/* Error */}
      {error && <p className="text-red-500 dark:text-red-400 text-sm">{error}</p>}

      {/* Preview with embed + format buttons */}
      {preview && (
        <div className="space-y-4">
          {/* YouTube iframe embed */}
          {videoId && (
            <div className="aspect-video rounded-xl overflow-hidden bg-black">
              <iframe
                src={`https://www.youtube.com/embed/${videoId}`}
                title={preview.title}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                loading="lazy"
              />
            </div>
          )}

          {/* Video info card */}
          <div className="rounded-xl p-4 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 flex gap-4 transition-colors">
            {preview.thumbnail && (
              <img src={preview.thumbnail} alt="" className="w-24 h-16 rounded-lg object-cover flex-shrink-0" />
            )}
            <div className="min-w-0">
              <p className="font-medium truncate">{preview.title}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">{preview.uploader}</p>
              {preview.duration > 0 && (
                <p className="text-xs text-slate-500 dark:text-slate-500">
                  {Math.floor(preview.duration / 60)}:{String(preview.duration % 60).padStart(2, '0')}
                </p>
              )}
            </div>
          </div>

          {/* Quality format buttons — like vidssave.com */}
          {videoFormats.length > 0 && (
            <div>
              <p className="text-sm font-medium text-slate-600 dark:text-slate-300 mb-3">
                Choose quality:
              </p>
              <div className="grid sm:grid-cols-2 gap-2">
                {/* "Highest" all-in-one option */}
                <button
                  onClick={() => handleDownload('Highest')}
                  disabled={loading}
                  className="flex items-center justify-between px-4 py-3 rounded-xl border-2 border-red-500 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/30 disabled:opacity-50 transition-colors text-left"
                >
                  <div>
                    <span className="font-semibold text-red-600 dark:text-red-400">Best Quality</span>
                    <p className="text-xs text-slate-500 dark:text-slate-400">Let us pick the best available</p>
                  </div>
                  <span className="text-xs font-medium text-green-600 dark:text-green-400 bg-green-100 dark:bg-green-900/30 px-2 py-0.5 rounded-full">
                    Recommended
                  </span>
                </button>

                {videoFormats.map((f) => {
                  const label = `${f.height}p`
                  const size = formatSize(f.filesize)
                  const isFast = f.height !== null && f.height <= 720
                  return (
                    <button
                      key={f.format_id}
                      onClick={() => handleDownload(label)}
                      disabled={loading}
                      className="flex items-center justify-between px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 hover:bg-slate-50 dark:hover:bg-slate-700/50 hover:border-slate-300 dark:hover:border-slate-600 disabled:opacity-50 transition-colors text-left"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-slate-800 dark:text-white">{label}</span>
                        <span className="text-xs text-slate-400 uppercase">{f.ext}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {size && <span className="text-xs text-slate-500 dark:text-slate-400">{size}</span>}
                        {isFast && (
                          <span className="text-xs font-medium text-blue-600 dark:text-blue-400 bg-blue-100 dark:bg-blue-900/30 px-1.5 py-0.5 rounded">
                            Fast
                          </span>
                        )}
                      </div>
                    </button>
                  )
                })}
              </div>
            </div>
          )}

          {videoFormats.length === 0 && (
            <button
              onClick={() => handleDownload('Highest')}
              disabled={loading}
              className="w-full px-6 py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
            >
              {loading ? 'Downloading...' : 'Download'}
            </button>
          )}
        </div>
      )}

      {/* Cancel button */}
      {taskId && (
        <button
          onClick={handleCancel}
          className="w-full py-2 text-sm text-slate-400 hover:text-red-500 transition-colors"
        >
          Cancel Download
        </button>
      )}

      {/* Progress */}
      <ProgressBar progress={progress} />

      {/* Download link */}
      {progress?.status === 'done' && taskId && (
        <a
          href={progress.download_url ? resolveApiUrl(progress.download_url) : getDownloadUrl(taskId, 'youtube')}
          className="block text-center px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-semibold transition-colors"
        >
          Download File
        </a>
      )}
    </div>
  )
}
