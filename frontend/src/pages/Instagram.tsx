import { useState, useRef, useCallback } from 'react'
import { startDownload, getProgress, getDownloadUrl, cancelTask, fetchInstagramStories, getProfilePicUrl, resolveApiUrl } from '../api/client.ts'
import type { ProgressState } from '../api/client.ts'
import ProgressBar from '../components/ProgressBar.tsx'
import AdUnit from '../components/AdUnit.tsx'

type Tab = 'post' | 'stories' | 'profile'

export default function InstagramPage() {
  const [tab, setTab] = useState<Tab>('post')

  return (
    <div className="space-y-6">
      <AdUnit className="mb-6" />

      <div className="max-w-xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Instagram Downloader
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Download posts, reels, stories & profile pictures</p>
        </div>

        {/* Sub-tabs */}
        <div className="flex gap-1 rounded-xl p-1 border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 transition-colors">
          {(['post', 'stories', 'profile'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                tab === t ? 'bg-purple-600 text-white' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white'
              }`}
            >
              {t === 'post' ? 'Post / Reel' : t}
            </button>
          ))}
        </div>

        {tab === 'post' && <PostReelDownload />}
        {tab === 'stories' && <StoriesDownload />}
        {tab === 'profile' && <ProfilePic />}
      </div>
    </div>
  )
}

function PostReelDownload() {
  const [url, setUrl] = useState('')
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
    <div className="space-y-4">
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

function StoriesDownload() {
  const [username, setUsername] = useState('')
  const [progress, setProgress] = useState<ProgressState | null>(null)
  const [taskId, setTaskId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current)
      pollingRef.current = null
    }
  }, [])

  const handleFetch = async () => {
    if (!username.trim()) { setError('Enter a username'); return }
    setError('')
    setProgress(null)
    setTaskId(null)
    stopPolling()
    setLoading(true)
    try {
      const { task_id } = await fetchInstagramStories(username.trim())
      setTaskId(task_id)
      pollingRef.current = setInterval(async () => {
        try {
          const p = await getProgress(task_id, 'instagram')
          setProgress(p)
          if (p.status === 'done' || p.status === 'error' || p.status === 'cancelled') {
            if (p.status === 'error' || p.status === 'cancelled') {
              setError(p.error_msg || `Stories download ${p.status}`)
            }
            stopPolling()
          }
        } catch (err) {
          setError(err instanceof Error ? err.message : 'Stories progress fetch failed')
          stopPolling()
        }
      }, 500)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stories')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="e.g. natgeo"
          className="w-full px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors"
        />
      </div>
      {error && <p className="text-red-500 dark:text-red-400 text-sm">{error}</p>}
      <button
        onClick={handleFetch}
        disabled={loading}
        className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
      >
        {loading ? 'Fetching...' : 'Fetch Stories'}
      </button>
      <ProgressBar progress={progress} />
      {progress?.status === 'done' && taskId && (
        <a
          href={progress.download_url ? resolveApiUrl(progress.download_url) : getDownloadUrl(taskId, 'instagram')}
          className="block text-center px-6 py-3 bg-green-600 hover:bg-green-500 text-white rounded-xl font-semibold transition-colors"
        >
          Download Stories File
        </a>
      )}
    </div>
  )
}

function ProfilePic() {
  const [username, setUsername] = useState('')
  const [picUrl, setPicUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleFetch = async () => {
    if (!username.trim()) { setError('Enter a username'); return }
    setError('')
    setPicUrl('')
    setLoading(true)
    try {
      const url = getProfilePicUrl(username.trim())
      // Verify it loads by checking headers
      const res = await fetch(url, { method: 'HEAD' })
      if (!res.ok) throw new Error('Profile picture not found')
      setPicUrl(url)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch profile picture')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">Username</label>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="e.g. natgeo"
          className="w-full px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-purple-500 transition-colors"
        />
      </div>
      {error && <p className="text-red-500 dark:text-red-400 text-sm">{error}</p>}
      <button
        onClick={handleFetch}
        disabled={loading}
        className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
      >
        {loading ? 'Fetching...' : 'Get Profile Picture'}
      </button>
      {picUrl && (
        <div className="flex flex-col items-center gap-3">
          <img src={picUrl} alt="Profile" className="w-32 h-32 rounded-full object-cover border-4 border-slate-200 dark:border-slate-700" />
          <a
            href={picUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 dark:text-blue-400 hover:text-blue-500 dark:hover:text-blue-300 text-sm underline"
          >
            Open full size
          </a>
        </div>
      )}
    </div>
  )
}
