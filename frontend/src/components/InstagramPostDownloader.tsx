import { useState, useRef, useCallback } from 'react'
import { startDownload, getProgress, getDownloadUrl, cancelTask, resolveApiUrl } from '../api/client.ts'
import type { ProgressState } from '../api/client.ts'
import ProgressBar from './ProgressBar.tsx'

interface InstagramPostDownloaderProps {
  initialUrl?: string
  className?: string
}

export default function InstagramPostDownloader({ initialUrl = '', className = '' }: InstagramPostDownloaderProps) {
  const [url, setUrl] = useState(initialUrl)
  const [progress, setProgress] = useState<ProgressState | null>(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
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
    setProgress(null)
    setTaskId(null)
    stopPolling()

    try {
      setLoading(true)
      const { task_id } = await startDownload({
        url: url.trim(),
        source: 'instagram',
      })
      setTaskId(task_id)
      setLoading(false)

      pollingRef.current = setInterval(async () => {
        try {
          const p = await getProgress(task_id, 'instagram')
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
      await cancelTask(taskId, 'instagram')
      stopPolling()
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleDownload()
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* URL Input */}
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">Post / Reel URL</label>
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="https://instagram.com/p/... or /reel/..."
          className="w-full px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors"
        />
      </div>

      {error && <p className="text-red-500 dark:text-red-400 text-sm">{error}</p>}

      <div className="flex gap-3">
        <button
          onClick={handleDownload}
          disabled={loading}
          className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
        >
          {loading ? 'Starting...' : 'Download'}
        </button>
        {taskId && (
          <button onClick={handleCancel} className="px-4 py-3 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-800 dark:text-white rounded-xl font-medium transition-colors">
            Cancel
          </button>
        )}
      </div>

      <ProgressBar progress={progress} />

      {progress?.status === 'done' && taskId && (
        <a
          href={progress.download_url ? resolveApiUrl(progress.download_url) : getDownloadUrl(taskId, 'instagram')}
          className="block text-center px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-semibold transition-colors"
        >
          Download File
        </a>
      )}
    </div>
  )
}
