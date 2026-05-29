import { useState, useEffect, type ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import AdUnit from './AdUnit.tsx'
import { ADS } from '../ads.ts'

const NAV = [
  { label: 'Home', path: '/' },
  { label: 'YouTube', path: '/youtube' },
  { label: 'Instagram', path: '/instagram' },
]

function useTheme() {
  const [dark, setDark] = useState(() => {
    const stored = localStorage.getItem('theme')
    if (stored) return stored === 'dark'
    return window.matchMedia('(prefers-color-scheme: dark)').matches
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return [dark, () => setDark((d) => !d)] as const
}

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()
  const [dark, toggleTheme] = useTheme()
  const [menuOpen, setMenuOpen] = useState(false)

  // Close menu on navigation
  useEffect(() => { setMenuOpen(false) }, [location.pathname])

  return (
    <div className="min-h-screen flex flex-col bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100 transition-colors">
      {/* Navbar */}
      <header className="border-b border-slate-200 dark:border-slate-800 bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50 transition-colors">
        <nav className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-amber-500 dark:text-amber-400 tracking-tight">
            InstaDownload
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
                  }`}
                >
                  {item.label}
                </Link>
              )
            })}
          </div>

          {/* Right: Theme toggle + Hamburger */}
          <div className="flex items-center gap-2">
            <button
              onClick={toggleTheme}
              aria-label="Toggle theme"
              className="p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              {dark ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              )}
            </button>

            {/* Mobile hamburger */}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Toggle menu"
              className="md:hidden p-2 rounded-lg text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                {menuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </nav>

        {/* Mobile nav dropdown */}
        {menuOpen && (
          <div className="md:hidden border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 transition-colors">
            <div className="px-4 py-2 space-y-1">
              {NAV.map((item) => {
                const isActive = location.pathname === item.path
                return (
                  <Link
                    key={item.path}
                    to={item.path}
                    className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      isActive
                        ? 'bg-blue-600 text-white'
                        : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                    }`}
                  >
                    {item.label}
                  </Link>
                )
              })}
            </div>
          </div>
        )}
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
        {children}
      </main>

      {/* Footer ad */}
      <div className="max-w-6xl mx-auto px-4 py-4">
        <AdUnit slot={ADS.FOOTER} />
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 pt-12 pb-8 text-sm text-slate-500 dark:text-slate-500 transition-colors">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 mb-10">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <Link to="/" className="text-lg font-bold text-amber-500 dark:text-amber-400 tracking-tight">
                InstaDownload
              </Link>
              <p className="mt-2 text-xs leading-relaxed text-slate-400 dark:text-slate-500">
                Download YouTube videos, MP3 audio, Instagram reels, posts, stories, and profile pictures — fast, free, and private.
              </p>
            </div>

            {/* Tools */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3">Tools</h3>
              <ul className="space-y-2">
                <li><Link to="/youtube" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">YouTube Downloader</Link></li>
                <li><Link to="/youtube-mp3" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">YouTube to MP3</Link></li>
                <li><Link to="/instagram" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Instagram Downloader</Link></li>
                <li><Link to="/instagram-story" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Instagram Story</Link></li>
              </ul>
            </div>

            {/* YouTube Guides */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3">YouTube Guides</h3>
              <ul className="space-y-2">
                <li><Link to="/youtube" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Download YouTube Videos</Link></li>
                <li><Link to="/youtube-mp3" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Convert YouTube to MP3</Link></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">Download 4K Videos</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">YouTube Shorts Downloader</span></li>
              </ul>
            </div>

            {/* Instagram Guides */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3">Instagram Guides</h3>
              <ul className="space-y-2">
                <li><Link to="/instagram" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Download Posts & Reels</Link></li>
                <li><Link to="/instagram-story" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Download Stories</Link></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">Download Profile Pictures</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">Download IGTV Videos</span></li>
              </ul>
            </div>

            {/* More Platforms */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3">More Platforms</h3>
              <ul className="space-y-2">
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">Facebook Downloader</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">TikTok Downloader</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">Pinterest Downloader</span></li>
              </ul>
            </div>

            {/* Legal & Support */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3">Legal</h3>
              <ul className="space-y-2">
                <li><Link to="/privacy" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Privacy Policy</Link></li>
                <li><Link to="/terms" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Terms of Service</Link></li>
                <li><Link to="/dmca" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">DMCA</Link></li>
                <li className="mt-3"><Link to="/contact" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors">Contact Us</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-200 dark:border-slate-800 pt-6 text-center text-xs text-slate-400 dark:text-slate-600">
            <p>&copy; {new Date().getFullYear()} InstaDownload. Built with yt-dlp. Not affiliated with YouTube or Instagram.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
