import { useState, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import AdUnit from '../components/AdUnit.tsx'

function detectSource(url: string): string | null {
  const u = url.toLowerCase().trim()
  if (/youtube\.com|youtu\.be/.test(u)) return '/youtube'
  if (/instagram\.com/.test(u)) return '/instagram'
  return null
}

export default function Home() {
  const navigate = useNavigate()
  const [url, setUrl] = useState('')

  const handlePaste = useCallback((e: React.ClipboardEvent) => {
    // Small delay to let the paste value settle
    setTimeout(() => {
      const el = e.target as HTMLInputElement
      const path = detectSource(el.value)
      if (path) navigate(path)
    }, 0)
  }, [navigate])

  const handleRedirect = () => {
    const path = detectSource(url)
    if (path) navigate(path)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') handleRedirect()
  }

  return (
    <div className="space-y-12">
      {/* Hero */}
      <section className="text-center py-16 space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
          Download from{' '}
          <span className="text-red-500">YouTube</span>{' '}
          <span className="text-pink-500">&amp;</span>{' '}
          <span className="text-purple-400">Instagram</span>
        </h1>
        <p className="text-lg text-slate-500 dark:text-slate-400 max-w-xl mx-auto">
          Fast, free, and private. Paste a link and download in seconds. No account needed.
        </p>

        {/* Paste URL bar */}
        <div className="max-w-lg mx-auto flex gap-2">
          <input
            type="text"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onPaste={handlePaste}
            onKeyDown={handleKeyDown}
            placeholder="Paste a YouTube or Instagram URL..."
            className="flex-1 px-4 py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
          />
          <button
            onClick={handleRedirect}
            className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors"
          >
            Go
          </button>
        </div>

        <div className="flex justify-center gap-4 pt-4">
          <Link
            to="/youtube"
            className="px-6 py-3 bg-red-600 hover:bg-red-500 text-white rounded-xl font-semibold transition-colors"
          >
            YouTube Downloader
          </Link>
          <Link
            to="/instagram"
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-500 hover:to-pink-500 text-white rounded-xl font-semibold transition-colors"
          >
            Instagram Downloader
          </Link>
        </div>
      </section>

      {/* Ad banner */}
      <AdUnit className="max-w-3xl mx-auto" />

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-6">
        {[
          { title: 'High Quality', desc: 'Download up to 4K resolution. Choose your preferred format and quality.' },
          { title: 'Audio Only', desc: 'Extract MP3 audio from any YouTube video at 192kbps.' },
          { title: 'Fast & Free', desc: 'Powered by yt-dlp. No limits, no sign-ups, no tracking.' },
        ].map((f) => (
          <div key={f.title} className="rounded-xl p-6 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 transition-colors">
            <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">{f.desc}</p>
          </div>
        ))}
      </section>

      {/* Bottom ad */}
      <AdUnit className="max-w-3xl mx-auto" />
    </div>
  )
}
