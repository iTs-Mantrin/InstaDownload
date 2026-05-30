import { useState, useRef, useCallback } from 'react'
import {
  fetchInstagramUserFeed,
  startDownload,
  getProgress,
  getDownloadUrl,
  cancelTask,
  resolveApiUrl,
} from '../api/client.ts'
import type { UserMediaItem, UserFeedResponse, ProgressState } from '../api/client.ts'
import ProgressBar from './ProgressBar.tsx'

// ── Types ─────────────────────────────────────────────────────

type FeedStatus = 'idle' | 'loading' | 'done' | 'error'

interface ItemDownloadState {
  taskId: string
  progress: ProgressState | null
  loading: boolean
  error: string
}

// ── Single grid item (manages its own download lifecycle) ─────

function FeedItem({ item }: { item: UserMediaItem }) {
  const [dl, setDl] = useState<ItemDownloadState | null>(null)
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  const handleDownload = async () => {
    if (dl && (dl.loading || (dl.progress?.status === 'running'))) return
    setDl({ taskId: '', progress: null, loading: true, error: '' })

    try {
      const { task_id } = await startDownload({ url: item.url, source: 'instagram' })
      setDl({ taskId: task_id, progress: null, loading: false, error: '' })

      pollingRef.current = setInterval(async () => {
        try {
          const p = await getProgress(task_id, 'instagram')
          setDl((prev) => prev ? { ...prev, progress: p } : null)
          if (p.status === 'done' || p.status === 'error' || p.status === 'cancelled') {
            if (p.status === 'error') {
              setDl((prev) => prev ? { ...prev, error: p.error_msg || 'Download failed' } : null)
            }
            stopPolling()
          }
        } catch {
          stopPolling()
        }
      }, 500)
    } catch (err) {
      setDl({ taskId: '', progress: null, loading: false, error: err instanceof Error ? err.message : 'Download failed' })
    }
  }

  const handleCancel = async () => {
    if (dl?.taskId) {
      await cancelTask(dl.taskId, 'instagram')
      stopPolling()
      setDl(null)
    }
  }

  const isRunning = dl?.loading || dl?.progress?.status === 'running' || dl?.progress?.status === 'downloading'
  const isDone = dl?.progress?.status === 'done'
  const imgSrc = item.thumbnail || `https://www.instagram.com/p/${item.id}/media/?size=l`

  return (
    <div className="group relative bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden shadow-sm hover:shadow-md transition-all duration-200">
      {/* Thumbnail */}
      <div className="aspect-[4/5] bg-slate-100 dark:bg-slate-700 overflow-hidden">
        <img
          src={imgSrc}
          alt={item.title}
          loading="lazy"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          onError={(e) => {
            (e.currentTarget as HTMLImageElement).style.display = 'none'
            const parent = (e.currentTarget as HTMLImageElement).parentElement
            if (parent) {
              parent.classList.add('flex', 'items-center', 'justify-center')
              parent.innerHTML = `
                <div class="flex flex-col items-center gap-2 text-slate-400 dark:text-slate-500">
                  <svg class="w-10 h-10" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5A2.25 2.25 0 0022.5 18.75V5.25A2.25 2.25 0 0020.25 3H3.75A2.25 2.25 0 001.5 5.25v13.5A2.25 2.25 0 003.75 21z" />
                  </svg>
                  <span class="text-xs">No thumbnail</span>
                </div>
              `
            }
          }}
        />
      </div>

      {/* Source badge */}
      <span
        className={`absolute top-2 left-2 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider rounded-md ${
          item.source === 'story'
            ? 'bg-pink-500/80 text-white'
            : 'bg-purple-500/80 text-white'
        }`}
      >
        {item.source === 'story' ? 'Story' : item.duration ? 'Reel' : 'Post'}
      </span>

      {/* Download button / progress */}
      <div className="p-3 space-y-2">
        <p className="text-xs text-slate-600 dark:text-slate-400 line-clamp-1 leading-relaxed">
          {item.title}
        </p>

        {isDone ? (
          <a
            href={dl!.progress!.download_url ? resolveApiUrl(dl!.progress!.download_url) : getDownloadUrl(dl!.taskId, 'instagram')}
            className="block w-full text-center px-3 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-sm font-semibold transition-colors"
          >
            Download File
          </a>
        ) : isRunning ? (
          <div className="space-y-1.5">
            <ProgressBar progress={dl!.progress} />
            {dl?.taskId && (
              <button
                onClick={handleCancel}
                className="w-full text-xs text-slate-500 dark:text-slate-400 hover:text-red-500 dark:hover:text-red-400 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
        ) : (
          <button
            onClick={handleDownload}
            disabled={dl?.loading}
            className="w-full px-3 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-lg text-sm font-semibold transition-colors"
          >
            {dl?.loading ? 'Starting...' : 'Download'}
          </button>
        )}

        {dl?.error && (
          <p className="text-xs text-red-500 dark:text-red-400">{dl.error}</p>
        )}
      </div>
    </div>
  )
}

// ── Main component ────────────────────────────────────────────

export default function InstagramUserFeed() {
  const [username, setUsername] = useState('')
  const [feed, setFeed] = useState<UserFeedResponse | null>(null)
  const [status, setStatus] = useState<FeedStatus>('idle')
  const [error, setError] = useState('')

  const handleFetch = async () => {
    const u = username.trim()
    if (!u) { setError('Enter a username'); return }
    setError('')
    setFeed(null)
    setStatus('loading')

    try {
      const result = await fetchInstagramUserFeed(u)
      setFeed(result)
      setStatus('done')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch user feed')
      setStatus('error')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleFetch()
  }

  return (
    <div className="space-y-4">
      {/* Input */}
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">
          Instagram Username
        </label>
        <div className="relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 font-medium">@</span>
          <input
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="username"
            className="w-full pl-8 pr-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors"
          />
        </div>
      </div>

      {error && (
        <p className="text-red-500 dark:text-red-400 text-sm">{error}</p>
      )}

      <button
        onClick={handleFetch}
        disabled={status === 'loading'}
        className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
      >
        {status === 'loading' ? 'Fetching...' : 'Fetch User Media'}
      </button>

      {/* Results */}
      {feed && (
        <div className="space-y-4 pt-2">
          <div className="flex items-center justify-between">
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Found <span className="font-semibold text-slate-800 dark:text-white">{feed.media_count}</span> item{feed.media_count !== 1 ? 's' : ''}
            </p>
          </div>

          {/* Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-3">
            {feed.media.map((item) => (
              <FeedItem key={item.id} item={item} />
            ))}
          </div>
        </div>
      )}

      {status === 'loading' && !feed && (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin" />
        </div>
      )}
    </div>
  )
}
