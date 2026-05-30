import { useState, useRef, useCallback, useEffect } from 'react'
import { fetchInstagramStories, getProgress, getDownloadUrl, resolveApiUrl } from '../api/client.ts'
import type { ProgressState } from '../api/client.ts'
import ProgressBar from '../components/ProgressBar.tsx'
import InstagramPostDownloader from '../components/InstagramPostDownloader.tsx'
import InstagramUserFeed from '../components/InstagramUserFeed.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'
import { useTranslation } from 'react-i18next'

const MAX_POLLS = 240
const POLL_INTERVAL_MS = 500

type Tab = 'post' | 'stories' | 'user'

export default function InstagramPage() {
  const { t } = useTranslation()
  const [tab, setTab] = useState<Tab>('post')

  const tabLabel: Record<Tab, string> = {
    post: t('instagram.tabPost', 'Post / Reel'),
    stories: t('instagram.tabStories', 'Stories'),
    user: t('instagram.tabProfile', 'User Feed'),
  }

  return (
    <div className="space-y-6">
      <AdUnit className="mb-6" slot={ADS.BANNER_TOP} />

      <div className="max-w-5xl mx-auto space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            {t('instagram.title', 'Instagram Downloader')}
          </h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">
            {t('instagram.subtitle', 'Download posts, reels & stories')}
          </p>
        </div>

        {/* Sub-tabs */}
        <div className="flex gap-1 rounded-xl p-1 border border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 transition-colors">
          {(['post', 'stories', 'user'] as const).map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={`flex-1 px-4 py-2 rounded-lg text-sm font-medium capitalize transition-colors ${
                tab === t ? 'bg-purple-600 text-white' : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-white'
              }`}
            >
              {tabLabel[t]}
            </button>
          ))}
        </div>

        {tab === 'post' && <InstagramPostDownloader />}
        {tab === 'stories' && <StoriesDownload />}
        {tab === 'user' && <InstagramUserFeed />}
      </div>

      <AdUnit className="max-w-3xl mx-auto" slot={ADS.IN_CONTENT} />

      <AdUnit className="max-w-3xl mx-auto mt-8" slot={ADS.BANNER_BOTTOM} />
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
  const pollCountRef = useRef<number>(0)
  const mountedRef = useRef<boolean>(true)

  // Cleanup on unmount
  useEffect(() => {
    mountedRef.current = true
    return () => {
      mountedRef.current = false
      if (pollingRef.current) {
        clearInterval(pollingRef.current)
        pollingRef.current = null
      }
    }
  }, [])

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
      pollCountRef.current = 0
      pollingRef.current = setInterval(async () => {
        pollCountRef.current++
        if (pollCountRef.current > MAX_POLLS) {
          stopPolling()
          if (mountedRef.current) {
            setError('Download timed out. The server may be experiencing issues.')
          }
          return
        }

        try {
          const p = await getProgress(task_id, 'instagram')
          if (!mountedRef.current) return
          setProgress(p)
          if (p.status === 'done' || p.status === 'error' || p.status === 'cancelled') {
            if (p.status === 'error' || p.status === 'cancelled') {
              setError(p.error_msg || `Stories download ${p.status}`)
            }
            stopPolling()
          }
        } catch (err) {
          if (!mountedRef.current) return
          setError(err instanceof Error ? err.message : 'Stories progress fetch failed')
          stopPolling()
        }
      }, POLL_INTERVAL_MS)
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


