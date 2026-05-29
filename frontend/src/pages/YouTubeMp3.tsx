import { useState, useRef, useCallback } from 'react'
import { startDownload, getProgress, getDownloadUrl, cancelTask, previewUrl, resolveApiUrl } from '../api/client.ts'
import type { ProgressState, PreviewInfo } from '../api/client.ts'
import ProgressBar from '../components/ProgressBar.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'
import Seo from '../components/Seo.tsx'

export default function YouTubeMp3() {
  const [url, setUrl] = useState('')
  const [quality, setQuality] = useState('192kbps')
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
    if (!url.trim()) { setError('Please enter a YouTube URL'); return }
    setError('')
    setPreview(null)
    setProgress(null)
    setTaskId(null)
    stopPolling()

    try {
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
        audio_only: true,
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

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleDownload()
  }

  return (
    <div className="space-y-12">
      <Seo
        title="YouTube to MP3 Converter - High Quality Audio Extraction"
        description="Convert YouTube videos to MP3 audio files for free. Choose from 128kbps, 192kbps, or 320kbps quality. Fast and easy to use."
        path="/youtube-to-mp3"
        keywords={['youtube to mp3', 'convert youtube to mp3', 'youtube audio downloader', 'extract audio from youtube']}
      />

      <AdUnit className="mb-6" slot={ADS.BANNER_TOP} />

      <div className="max-w-xl mx-auto space-y-8">
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold tracking-tight">YouTube to MP3 Converter</h1>
          <p className="text-slate-500 dark:text-slate-400">Extract high-quality audio from any YouTube video</p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">YouTube Video URL</label>
            <input
              type="text"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="https://www.youtube.com/watch?v=..."
              className="w-full px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <label className="block text-sm font-medium mb-1.5 text-slate-600 dark:text-slate-300">Audio Quality</label>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
                className="w-full px-3 py-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors"
              >
                <option value="128kbps">128kbps (Standard)</option>
                <option value="192kbps">192kbps (High)</option>
                <option value="320kbps">320kbps (Ultra)</option>
              </select>
            </div>
            <button
              onClick={handleDownload}
              disabled={loading}
              className="sm:mt-6 px-8 py-3 bg-red-600 hover:bg-red-500 disabled:opacity-50 text-white rounded-xl font-semibold transition-colors"
            >
              {loading ? 'Processing...' : 'Convert to MP3'}
            </button>
          </div>
        </div>

        {preview && (
          <div className="rounded-xl p-4 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 flex gap-4 transition-colors animate-in fade-in slide-in-from-bottom-2">
            {preview.thumbnail && (
              <img src={preview.thumbnail} alt="" className="w-24 h-16 rounded-lg object-cover flex-shrink-0" />
            )}
            <div className="min-w-0">
              <p className="font-medium truncate">{preview.title}</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">{preview.uploader}</p>
            </div>
          </div>
        )}

        {error && <p className="text-red-500 dark:text-red-400 text-sm text-center">{error}</p>}

        <ProgressBar progress={progress} />

        {progress?.status === 'done' && taskId && (
          <div className="space-y-4">
            <a
              href={progress.download_url ? resolveApiUrl(progress.download_url) : getDownloadUrl(taskId, 'youtube')}
              className="block text-center px-6 py-4 bg-green-600 hover:bg-green-500 text-white rounded-xl font-bold text-lg transition-colors shadow-lg shadow-green-500/20"
            >
              Download MP3
            </a>
            <button
              onClick={() => { setUrl(''); setProgress(null); setPreview(null); setTaskId(null); }}
              className="w-full text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
            >
              Convert another video
            </button>
          </div>
        )}

        {taskId && progress?.status !== 'done' && (
          <button
            onClick={handleCancel}
            className="w-full py-2 text-sm text-slate-400 hover:text-red-500 transition-colors"
          >
            Cancel Conversion
          </button>
        )}
      </div>

      <AdUnit className="max-w-3xl mx-auto" slot={ADS.BANNER_BOTTOM} />

      <section className="max-w-3xl mx-auto prose dark:prose-invert">
        <h2 className="text-2xl font-bold mb-4">How to Convert YouTube to MP3</h2>
        <ol className="space-y-4 list-decimal pl-5">
          <li>
            <strong>Copy the URL:</strong> Go to YouTube and copy the link of the video you want to convert to audio.
          </li>
          <li>
            <strong>Paste the Link:</strong> Paste the YouTube URL into the input field at the top of this page.
          </li>
          <li>
            <strong>Select Quality:</strong> Choose your preferred MP3 quality (128kbps, 192kbps, or 320kbps).
          </li>
          <li>
            <strong>Convert:</strong> Click the "Convert to MP3" button to start the extraction process.
          </li>
          <li>
            <strong>Download:</strong> Once the conversion is complete, click the "Download MP3" button to save the file to your device.
          </li>
        </ol>

        <h3 className="text-xl font-bold mt-8 mb-4">Why use our YouTube to MP3 Converter?</h3>
        <ul className="space-y-2 list-disc pl-5">
          <li>Fast and reliable conversion powered by advanced technology.</li>
          <li>No registration or software installation required.</li>
          <li>Completely free to use with no hidden limits.</li>
          <li>High-quality audio output up to 320kbps.</li>
          <li>Mobile-friendly interface for downloading on the go.</li>
        </ul>
      </section>
    </div>
  )
}
