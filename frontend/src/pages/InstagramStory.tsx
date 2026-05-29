import { useState, useRef, useCallback } from 'react'
import { fetchInstagramStories, getProgress, getDownloadUrl, resolveApiUrl } from '../api/client.ts'
import type { ProgressState } from '../api/client.ts'
import ProgressBar from '../components/ProgressBar.tsx'
import AdUnit from '../components/AdUnit.tsx'
import Seo from '../components/Seo.tsx'

export default function InstagramStory() {
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
    if (!username.trim()) { setError('Please enter an Instagram username'); return }
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleFetch()
  }

  return (
    <div className="space-y-12">
      <Seo
        title="Instagram Story Downloader - Download Stories Anonymously"
        description="Download Instagram stories and highlights for free. Just enter the username and fetch all active stories. Fast, private, and easy."
        path="/instagram-story-downloader"
        keywords={['instagram story downloader', 'download instagram stories', 'instagram story saver', 'anonymous story viewer']}
      />

      <AdUnit className="mb-6" />

      <div className="max-w-xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text text-transparent">
            Instagram Story Downloader
          </h1>
          <p className="text-slate-500 dark:text-slate-400">Download active stories from any public Instagram account</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">Instagram Username</label>
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

          <button
            onClick={handleFetch}
            disabled={loading}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors shadow-lg shadow-purple-500/20"
          >
            {loading ? 'Fetching Stories...' : 'Fetch Stories'}
          </button>
        </div>

        {error && <p className="text-red-500 dark:text-red-400 text-sm text-center">{error}</p>}

        <ProgressBar progress={progress} />

        {progress?.status === 'done' && taskId && (
          <div className="space-y-4">
            <a
              href={progress.download_url ? resolveApiUrl(progress.download_url) : getDownloadUrl(taskId, 'instagram')}
              className="block text-center px-6 py-4 bg-green-600 hover:bg-green-500 text-white rounded-xl font-bold text-lg transition-colors shadow-lg shadow-green-500/20"
            >
              Download Stories Archive
            </a>
            <p className="text-center text-xs text-slate-500">
              All active stories have been bundled into a single ZIP file for your convenience.
            </p>
          </div>
        )}
      </div>

      <AdUnit className="max-w-3xl mx-auto" />

      <section className="max-w-3xl mx-auto prose dark:prose-invert">
        <h2 className="text-2xl font-bold mb-4">How to Download Instagram Stories</h2>
        <ol className="space-y-4 list-decimal pl-5">
          <li>
            <strong>Enter Username:</strong> Type the Instagram username (without the @ symbol) into the input field.
          </li>
          <li>
            <strong>Fetch Stories:</strong> Click the "Fetch Stories" button. Our system will look for active stories on that account.
          </li>
          <li>
            <strong>Wait for Processing:</strong> The downloader will gather all available stories and prepare them for download.
          </li>
          <li>
            <strong>Download:</strong> Once ready, click the "Download Stories Archive" button to save all stories as a ZIP file.
          </li>
        </ol>

        <h3 className="text-xl font-bold mt-8 mb-4">Features of our Story Downloader</h3>
        <ul className="space-y-2 list-disc pl-5">
          <li><strong>Anonymous:</strong> The account owner will not know you viewed or downloaded their stories.</li>
          <li><strong>High Quality:</strong> Stories are downloaded in their original resolution and format.</li>
          <li><strong>Fast:</strong> Quick fetching and processing of multiple stories at once.</li>
          <li><strong>Free:</strong> No subscription or payment required to use the service.</li>
          <li><strong>Public Accounts:</strong> Works with any public Instagram account.</li>
        </ul>
      </section>
    </div>
  )
}
