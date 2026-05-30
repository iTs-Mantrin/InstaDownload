import { useState } from 'react'
import { Link } from 'react-router-dom'
import YouTubeDownloader from '../components/YouTubeDownloader.tsx'
import InstagramPostDownloader from '../components/InstagramPostDownloader.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'
import Seo from '../components/Seo.tsx'

type DetectedSource = 'youtube' | 'instagram' | null

function detectSource(url: string): DetectedSource {
  const u = url.toLowerCase().trim()
  if (/youtube\.com|youtu\.be/.test(u)) return 'youtube'
  if (/instagram\.com/.test(u)) return 'instagram'
  return null
}

const TOOLS = [
  {
    label: 'YouTube',
    path: '/youtube',
    color: 'red',
    gradient: 'from-red-600 to-red-500',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
      </svg>
    ),
  },
  {
    label: 'YouTube MP3',
    path: '/youtube-mp3',
    color: 'orange',
    gradient: 'from-orange-500 to-red-500',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
      </svg>
    ),
  },
  {
    label: 'Instagram',
    path: '/instagram',
    color: 'purple',
    gradient: 'from-purple-600 to-pink-500',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
        <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
      </svg>
    ),
  },
  {
    label: 'Instagram Story',
    path: '/instagram-story',
    color: 'pink',
    gradient: 'from-pink-500 to-rose-500',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
      </svg>
    ),
  },
]

const STEPS = [
  {
    num: '1',
    title: 'Copy the URL',
    desc: 'Open YouTube or Instagram, find the video, reel, or photo you want, and copy its link.',
  },
  {
    num: '2',
    title: 'Paste the link',
    desc: 'Paste the URL into the input field above. Our tool will auto-detect the source and show a preview.',
  },
  {
    num: '3',
    title: 'Download',
    desc: 'Choose your preferred quality and click the Download button. The file is saved directly to your device.',
  },
]

const FEATURES = [
  {
    title: 'High Quality',
    desc: 'Download up to 4K resolution. Choose your preferred format and quality.',
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
    ),
    iconColor: 'text-green-500',
  },
  {
    title: 'Audio Only',
    desc: 'Extract MP3 audio from any YouTube video at up to 320kbps quality.',
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
      </svg>
    ),
    iconColor: 'text-blue-500',
  },
  {
    title: 'Fast & Free',
    desc: 'Powered by yt-dlp. No limits, no sign-ups, no tracking. Completely free to use.',
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
      </svg>
    ),
    iconColor: 'text-amber-500',
  },
]

const PLATFORMS = [
  {
    name: 'YouTube',
    path: '/youtube',
    color: 'text-red-500',
    gradient: 'from-red-500 to-red-600',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
        <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
      </svg>
    ),
  },
  {
    name: 'Instagram',
    path: '/instagram',
    color: 'text-pink-500',
    gradient: 'from-purple-500 to-pink-500',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
        <rect x="2" y="2" width="20" height="20" rx="5" ry="5" />
        <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z" />
        <line x1="17.5" y1="6.5" x2="17.51" y2="6.5" />
      </svg>
    ),
  },
  {
    name: 'Facebook',
    color: 'text-blue-600',
    gradient: 'from-blue-600 to-blue-700',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
        <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
      </svg>
    ),
  },
  {
    name: 'TikTok',
    color: 'text-slate-800 dark:text-white',
    gradient: 'from-slate-700 to-slate-900',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z" />
      </svg>
    ),
  },
  {
    name: 'Pinterest',
    color: 'text-red-700',
    gradient: 'from-red-700 to-red-800',
    svg: (
      <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
        <path d="M12.017 0C5.396 0 .029 5.367.029 11.987c0 5.079 3.158 9.417 7.618 11.162-.105-.949-.199-2.403.041-3.439.219-.937 1.406-5.957 1.406-5.957s-.359-.72-.359-1.782c0-1.67.968-2.914 2.172-2.914 1.027 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 0 1 .083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.631-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146 1.124.347 2.317.535 3.554.535 6.607 0 11.972-5.365 11.972-11.987C23.97 5.367 18.607 0 12.017 0z" />
      </svg>
    ),
  },
]

export default function Home() {
  const [url, setUrl] = useState('')
  const [source, setSource] = useState<DetectedSource>(null)

  const handlePasteEvent = (e: React.ClipboardEvent) => {
    setTimeout(() => {
      const el = e.target as HTMLInputElement
      const val = el.value
      setUrl(val)
      const s = detectSource(val)
      if (s) setSource(s)
    }, 0)
  }

  const handlePasteClick = async () => {
    try {
      const text = await navigator.clipboard.readText()
      setUrl(text)
      const s = detectSource(text)
      if (s) setSource(s)
    } catch {
      // clipboard permission denied or not available
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      const s = detectSource(url)
      if (s) setSource(s)
    }
  }

  const handleClear = () => {
    setUrl('')
    setSource(null)
  }

  return (
    <div className="space-y-16">
      <Seo
        title="InstaDownload - YouTube & Instagram Downloader"
        description="Download YouTube videos, MP3 audio, Instagram reels, posts, and stories with a fast mobile-first UI."
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
      <section className="text-center pt-16 md:pt-24 pb-4 space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight leading-tight">
          Free All-in-One{' '}
          <span className="bg-gradient-to-r from-red-500 via-purple-500 to-blue-600 bg-clip-text text-transparent">
            Video Downloader
          </span>
        </h1>
        <p className="text-lg text-slate-500 dark:text-slate-400 max-w-2xl mx-auto">
          Download videos, reels, stories, and audio from YouTube, Instagram, Facebook, TikTok, and more.
          Fast, free, and private. No account needed.
        </p>

        {/* Paste URL bar with Paste button */}
        <div className="max-w-xl mx-auto">
          <div className="flex gap-2">
            <div className="relative flex-1">
              <input
                type="text"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                onPaste={handlePasteEvent}
                onKeyDown={handleKeyDown}
                placeholder="Paste a YouTube or Instagram URL..."
                className="w-full pl-4 pr-[4.5rem] py-3 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
              />
              <button
                onClick={handlePasteClick}
                className="absolute right-1.5 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-slate-200 dark:bg-slate-700 hover:bg-slate-300 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 rounded-lg text-sm font-medium transition-colors flex items-center gap-1.5"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
                Paste
              </button>
            </div>
            <button
              onClick={() => { const s = detectSource(url); if (s) setSource(s) }}
              className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors"
            >
              Go
            </button>
          </div>
        </div>
      </section>

      {/* Tool categories — like sssinstagram service nav */}
      <section className="max-w-3xl mx-auto">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {TOOLS.map((tool) => (
            <Link
              key={tool.path}
              to={tool.path}
              className="flex flex-col items-center gap-2 p-5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 hover:shadow-md hover:-translate-y-0.5 transition-all group"
            >
              <span className={`bg-gradient-to-br ${tool.gradient} text-white p-3 rounded-xl`}>
                {tool.svg}
              </span>
              <span className="text-sm font-semibold text-slate-700 dark:text-slate-300 group-hover:text-slate-900 dark:group-hover:text-white transition-colors">
                {tool.label}
              </span>
            </Link>
          ))}
        </div>
      </section>

      {/* Inline downloader when URL detected */}
      {source === 'youtube' && (
        <section className="max-w-xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-red-500">YouTube Download</h2>
            <button
              onClick={handleClear}
              className="text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
            >
              Clear
            </button>
          </div>
          <YouTubeDownloader initialUrl={url} />
        </section>
      )}

      {source === 'instagram' && (
        <section className="max-w-xl mx-auto">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-transparent bg-gradient-to-r from-purple-500 to-pink-500 bg-clip-text">
              Instagram Download
            </h2>
            <button
              onClick={handleClear}
              className="text-sm text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
            >
              Clear
            </button>
          </div>
          <InstagramPostDownloader initialUrl={url} />
        </section>
      )}

      {/* Default content — only when no URL detected */}
      {!source && (
        <>
          <AdUnit className="max-w-3xl mx-auto" slot={ADS.BANNER_TOP} />

          {/* Platform support grid — like vidssave.com */}
          <section className="max-w-3xl mx-auto space-y-6">
            <h2 className="text-2xl font-bold text-center">Supported Platforms</h2>
            <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
              {PLATFORMS.map((p) => (
                <div
                  key={p.name}
                  className="flex flex-col items-center gap-3 p-5 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 hover:shadow-md hover:-translate-y-0.5 transition-all group text-center"
                >
                  <span className={`bg-gradient-to-br ${p.gradient} text-white p-3.5 rounded-2xl`}>
                    {p.svg}
                  </span>
                  <span className="text-sm font-medium text-slate-600 dark:text-slate-400">
                    {p.name}
                  </span>
                </div>
              ))}
            </div>
          </section>

          {/* How-to section */}
          <section className="max-w-3xl mx-auto space-y-8">
            <h2 className="text-2xl font-bold text-center">How to download?</h2>
            <div className="grid md:grid-cols-3 gap-4">
              {STEPS.map((step) => (
                <div
                  key={step.num}
                  className="relative rounded-xl p-6 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 text-center transition-colors"
                >
                  <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-600 text-white text-lg font-bold mb-4">
                    {step.num}
                  </span>
                  <h3 className="text-lg font-semibold mb-2">{step.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{step.desc}</p>
                </div>
              ))}
            </div>
          </section>

          {/* Features */}
          <section className="grid md:grid-cols-3 gap-6">
            {FEATURES.map((f) => (
              <div
                key={f.title}
                className="rounded-xl p-6 border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800/50 transition-colors"
              >
                <div className={`w-11 h-11 rounded-lg flex items-center justify-center bg-slate-100 dark:bg-slate-700 ${f.iconColor} mb-4`}>
                  {f.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{f.desc}</p>
              </div>
            ))}
          </section>

          <AdUnit className="max-w-3xl mx-auto" slot={ADS.BANNER_BOTTOM} />

          <AdUnit className="max-w-3xl mx-auto" slot={ADS.IN_CONTENT} />

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
                { q: 'What platforms do you support?', a: 'We currently support YouTube, Instagram, Facebook, TikTok, and Pinterest. More platforms coming soon!' },
                { q: 'Does Instagram support stories?', a: 'Yes, you can download Instagram stories by entering a username. Note: stories require the account to not be private.' },
                { q: 'Can I download all reels and posts from an Instagram user?', a: 'Yes! Use the User Feed feature on the Instagram page — enter any username to browse and download all their reels, posts, and stories with individual download buttons.' },
                { q: 'Can I download Facebook videos?', a: 'Facebook video download is coming soon. In the meantime, try our YouTube or Instagram downloaders.' },
                { q: 'Can I download TikTok videos?', a: 'TikTok video download is coming soon. Our platform will support downloading TikTok videos without watermarks.' },
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
        </>
      )}
    </div>
  )
}
