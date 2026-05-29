import { useState, useRef, useCallback } from 'react'
import { startDownload, getProgress, getDownloadUrl, cancelTask, previewUrl } from '../api/client.ts'
import type { ProgressState, PreviewInfo } from '../api/client.ts'
import ProgressBar from '../components/ProgressBar.tsx'

export default function YouTubePage() {
  const [url, setUrl] = useState('')
  const [quality, setQuality] = useState('Highest')
  const [audioOnly, setAudioOnly] = useState(false)
  const [progress, setProgress] = useState<ProgressState | null>(null)
  const [preview, setPreview] = useState<PreviewInfo | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [taskId, setTaskId] = useState<string | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  const handleDownload = async () => {
    if (!url.trim()) { setError('Please enter a URL'); return }
    setError('')
    setPreview(null)
    setProgress(null)
    setTaskId(null)
    stopPolling()

    try {
      // Preview
      try {
        const info = await previewUrl(url.trim(), 'youtube')
        setPreview(info)
      } catch {
        // preview is optional
      }

      setLoading(true)
      const { task_id } = await startDownload({
        url: url.trim(),
        source: 'youtube',
        quality,
        audio_only: audioOnly,
      })
      setTaskId(task_id)
      setLoading(false)

      // Start polling
      pollingRef.current = setInterval(async () => {
        try {
          const p = await getProgress(task_id)
          setProgress(p)
          if (p.status === 'done' || p.status === 'error' || p.status === 'cancelled') {
            stopPolling()
          }
        } catch {
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
      await cancelTask(taskId)
      stopPolling()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleDownload()
  }

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-3xl font-bold">YouTube Downloader</h1>
        <p className="text-slate-400 mt-1">Download videos or extract audio</p>
      </div>

      {/* URL Input */}
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-300">Video URL</label>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="https://youtube.com/watch?v=... or https://youtu.be/..."
          className="w-full px-4 py-3 rounded-xl bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Options */}
      <div className="flex gap-4 items-end flex-wrap">
        <div className="flex-1 min-w-[140px]">
          <label className="block text-sm font-medium mb-1.5 text-slate-300">Quality</label>
          <select
            value={quality}
            onChange={(e) => setQuality(e.target.value)}
            className="w-full px-3 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="Highest">Highest</option>
            <option value="1080p">1080p</option>
            <option value="720p">720p</option>
            <option value="480p">480p</option>
            <option value="360p">360p</option>
          </select>
        </div>

        <label className="flex items-center gap-2 cursor-pointer pb-1">
          <input
            type="checkbox"
            checked={audioOnly}
            onChange={(e) => setAudioOnly(e.target.checked)}
            className="w-4 h-4 rounded border-slate-600 bg-slate-800"
          />
          <span className="text-sm text-slate-300">Audio only (MP3)</span>
        </label>
      </div>

      {/* Preview */}
      {preview && (
        <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 flex gap-4">
          {preview.thumbnail && (
            <img src={preview.thumbnail} alt="" className="w-24 h-16 rounded-lg object-cover flex-shrink-0" />
          )}
          <div className="min-w-0">
            <p className="font-medium truncate">{preview.title}</p>
            <p className="text-sm text-slate-400">{preview.uploader}</p>
            {preview.duration > 0 && (
              <p className="text-xs text-slate-500">
                {Math.floor(preview.duration / 60)}:{String(preview.duration % 60).padStart(2, '0')}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Error */}
      {error && <p className="text-red-400 text-sm">{error}</p>}

      {/* Actions */}
      <div className="flex gap-3">
        <button
          onClick={handleDownload}
          disabled={loading}
          className="flex-1 px-6 py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
        >
          {loading ? 'Starting...' : 'Download'}
        </button>
        {taskId && (
          <button
            onClick={handleCancel}
            className="px-4 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl font-medium transition-colors"
          >
            Cancel
          </button>
        )}
      </div>

      {/* Progress */}
      <ProgressBar progress={progress} />

      {/* Download link */}
      {progress?.status === 'done' && taskId && (
        <a
          href={getDownloadUrl(taskId)}
          className="block text-center px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-semibold transition-colors"
        >
          Download File
        </a>
      )}
    </div>
  )
}
