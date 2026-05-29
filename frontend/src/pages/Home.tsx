import { useState, useCallback } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'
import Seo from '../components/Seo.tsx'

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
      <Seo
        title="InstaDownload - YouTube & Instagram Downloader"
        description="Download YouTube videos, MP3 audio, Instagram reels, posts, stories, and profile pictures with a fast mobile-first UI."
        path="/"
        keywords={['youtube downloader', 'instagram downloader', 'youtube to mp3', 'instagram reels downloader']}
        schema={{
          '@context': 'https://schema.org',
          '@type': 'WebApplication',
          name: 'InstaDownload',
          applicationCategory: 'MultimediaApplication',
          operatingSystem: 'Web',
          description: 'Download YouTube and Instagram media with previews, progress tracking, and mobile-first UX.',
        }}
      />

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
      <AdUnit className="max-w-3xl mx-auto" slot={ADS.BANNER_TOP} />

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
      <AdUnit className="max-w-3xl mx-auto" slot={ADS.BANNER_BOTTOM} />

      {/* FAQ */}
      <section className="max-w-3xl mx-auto space-y-6">
        <h2 className="text-2xl font-bold text-center">Frequently Asked Questions</h2>
        <div className="space-y-3">
          {[
            { q: 'Is InstaDownload free?', a: 'Yes, completely free. No sign-ups, no hidden costs, no premium tiers.' },
            { q: 'Do I need an account?', a: 'No account or login required. Just paste a link and download.' },
            { q: 'What quality options are available?', a: 'YouTube: up to 1080p (and 4K if available). Choose from 360p, 480p, 720p, 1080p, or Highest. Instagram: best available quality.' },
            { q: 'Can I download just the audio?', a: 'Yes! Use the YouTube MP3 option to extract audio at 128-320kbps.' },
            { q: 'How long are files stored?', a: 'Downloaded files are automatically deleted from our servers within 30 minutes for your privacy.' },
            { q: 'Is it safe?', a: 'All connections are encrypted via HTTPS. We don\'t track, store, or share your downloads.' },
            { q: 'Does Instagram support stories?', a: 'Yes, you can download Instagram stories by entering a username. Note: stories require the account to not be private.' },
            { q: 'Can I download Instagram profile pictures?', a: 'Yes! Enter any Instagram username and we\'ll fetch their current profile picture in HD.' },
          ].map((faq) => (
            <details key={faq.q} className="group rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 transition-colors">
              <summary className="px-5 py-4 font-medium text-slate-900 dark:text-white cursor-pointer list-none flex items-center justify-between">
                {faq.q}
                <svg className="w-5 h-5 text-slate-400 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <p className="px-5 pb-4 text-sm text-slate-600 dark:text-slate-400">{faq.a}</p>
            </details>
          ))}
        </div>
      </section>
    </div>
  )
}
