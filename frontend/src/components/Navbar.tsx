import { useState, useEffect, useRef, type ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import LanguageSwitcher from './LanguageSwitcher.tsx'

// ── Icons ────────────────────────────────────────────────────

function HomeIcon() {
  return (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
    </svg>
  )
}

function YouTubeIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
    </svg>
  )
}

function InstagramIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
    </svg>
  )
}

function FacebookIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
    </svg>
  )
}

function TikTokIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z" />
    </svg>
  )
}

function PinterestIcon() {
  return (
    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.373 0 0 5.372 0 12c0 5.084 3.163 9.426 7.627 11.174-.105-.949-.2-2.403.042-3.438.218-.932 1.407-5.965 1.407-5.965s-.359-.719-.359-1.782c0-1.668.967-2.914 2.171-2.914 1.023 0 1.518.769 1.518 1.69 0 1.029-.655 2.568-.994 3.995-.283 1.194.599 2.169 1.777 2.169 2.133 0 3.772-2.249 3.772-5.495 0-2.873-2.064-4.882-5.012-4.882-3.414 0-5.418 2.561-5.418 5.207 0 1.031.397 2.138.893 2.738a.36.36 0 01.083.345l-.333 1.36c-.053.22-.174.267-.402.161-1.499-.698-2.436-2.889-2.436-4.649 0-3.785 2.75-7.262 7.929-7.262 4.163 0 7.398 2.967 7.398 6.931 0 4.136-2.607 7.464-6.227 7.464-1.216 0-2.359-.631-2.75-1.378l-.748 2.853c-.271 1.043-1.002 2.35-1.492 3.146C9.57 23.812 10.763 24 12 24c6.627 0 12-5.373 12-12 0-6.628-5.373-12-12-12z" />
    </svg>
  )
}

// ── Nav data ─────────────────────────────────────────────────

interface NavChild {
  labelKey: string
  path: string
  group?: string
}

interface NavItem {
  icon: ReactNode
  labelKey: string
  path?: string
  children?: NavChild[]
  disabled?: boolean
}

const NAV_ITEMS: NavItem[] = [
  { icon: <HomeIcon />, labelKey: 'nav.home', path: '/' },
  {
    icon: <YouTubeIcon />,
    labelKey: 'nav.youtube',
    path: '/youtube',
    children: [
      { labelKey: 'nav.youtubeSub.downloader', path: '/youtube', group: 'download' },
      { labelKey: 'nav.youtubeSub.videoDownloader', path: '/youtube', group: 'download' },
      { labelKey: 'nav.youtubeSub.shortsDownloader', path: '/youtube', group: 'download' },
      { labelKey: 'nav.youtubeSub.mp3', path: '/youtube-mp3', group: 'audio' },
      { labelKey: 'nav.youtubeSub.audioDownloader', path: '/youtube-mp3', group: 'audio' },
      { labelKey: 'nav.youtubeSub.songDownloader', path: '/youtube-mp3', group: 'audio' },
      { labelKey: 'nav.youtubeSub.toMp4', path: '/youtube', group: 'more' },
      { labelKey: 'nav.youtubeSub.musicDownloader', path: '/youtube-mp3', group: 'more' },
      { labelKey: 'nav.youtubeSub.moviesDownloader', path: '/youtube', group: 'more' },
    ],
  },
  {
    icon: <InstagramIcon />,
    labelKey: 'nav.instagram',
    path: '/instagram',
    children: [
      { labelKey: 'nav.instagramSub.downloader', path: '/instagram', group: 'download' },
      { labelKey: 'nav.instagramSub.videoDownloader', path: '/instagram', group: 'download' },
      { labelKey: 'nav.instagramSub.photoDownloader', path: '/instagram', group: 'download' },
      { labelKey: 'nav.instagramSub.reelsDownloader', path: '/instagram', group: 'social' },
      { labelKey: 'nav.instagramSub.story', path: '/instagram-story', group: 'social' },
      { labelKey: 'nav.instagramSub.carouselDownloader', path: '/instagram', group: 'more' },
      { labelKey: 'nav.instagramSub.profileDownloader', path: '/instagram', group: 'more' },
    ],
  },
  { icon: <FacebookIcon />, labelKey: 'nav.facebook', disabled: true },
  { icon: <TikTokIcon />, labelKey: 'nav.tiktok', disabled: true },
  { icon: <PinterestIcon />, labelKey: 'nav.pinterest', disabled: true },
]

const GROUP_LABELS: Record<string, string> = {
  download: 'Download',
  audio: 'Audio',
  social: 'Stories & Reels',
  more: 'More',
}

// ── Helpers ──────────────────────────────────────────────────

function isActive(path: string | undefined, currentPath: string): boolean {
  if (!path) return false
  if (path === '/') return currentPath === '/'
  return currentPath.startsWith(path)
}

function childActive(children: NavChild[] | undefined, currentPath: string): boolean {
  if (!children) return false
  return children.some((c) => isActive(c.path, currentPath))
}

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

function useScrollHide() {
  const [visible, setVisible] = useState(true)
  const lastY = useRef(0)
  useEffect(() => {
    const THRESHOLD = 10
    const handler = () => {
      const currentY = window.scrollY
      const delta = currentY - lastY.current
      if (Math.abs(delta) < THRESHOLD) { lastY.current = currentY; return }
      if (delta > 0 && currentY > 80) setVisible(false)
      else if (delta < 0) setVisible(true)
      lastY.current = currentY
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])
  return visible
}

function useScrollProgress() {
  const [progress, setProgress] = useState(0)
  useEffect(() => {
    const handler = () => {
      const scrollTop = window.scrollY
      const docHeight = document.documentElement.scrollHeight - window.innerHeight
      setProgress(docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0)
    }
    window.addEventListener('scroll', handler, { passive: true })
    return () => window.removeEventListener('scroll', handler)
  }, [])
  return progress
}

// ── Desktop Nav Item ─────────────────────────────────────────

function DesktopNavItem({
  item,
  currentPath,
  isDisabled,
}: {
  item: NavItem
  currentPath: string
  isDisabled: boolean
}) {
  const { t } = useTranslation()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const active =
    !isDisabled && (isActive(item.path, currentPath) || childActive(item.children, currentPath))
  const hasDropdown = !!item.children && !isDisabled

  // Group children
  const groups = item.children
    ? item.children.reduce<Record<string, NavChild[]>>((acc, child) => {
        const g = child.group ?? 'default'
        if (!acc[g]) acc[g] = []
        acc[g].push(child)
        return acc
      }, {})
    : null

  const linkClasses = `relative flex items-center gap-1.5 px-3 py-2 text-sm font-medium transition-colors duration-150 whitespace-nowrap ${
    isDisabled
      ? 'text-slate-300 dark:text-slate-600 cursor-default'
      : active
        ? 'text-blue-600 dark:text-blue-400'
        : 'text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white'
  }`

  const content = (
    <>
      <span className="shrink-0">{item.icon}</span>
      <span>{t(item.labelKey)}</span>
      {hasDropdown && (
        <svg
          className={`w-3 h-3 mt-0.5 transition-transform duration-200 ${dropdownOpen ? 'rotate-180' : ''}`}
          fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
        </svg>
      )}
    </>
  )

  if (isDisabled) {
    return <div className={linkClasses}>{content}</div>
  }

  return (
    <div
      className="relative"
      onMouseEnter={() => setDropdownOpen(true)}
      onMouseLeave={() => setDropdownOpen(false)}
    >
      <Link to={item.path ?? '#'} className={linkClasses}>
        {content}
      </Link>

      {/* Active bottom border */}
      {active && (
        <span className="absolute bottom-0 left-3 right-3 h-0.5 bg-blue-600 dark:bg-blue-400 rounded-full" />
      )}

      {/* Dropdown */}
      {hasDropdown && groups && (
        <div
          className={`absolute left-0 mt-1.5 w-64 transition-all duration-200 z-50 ${
            dropdownOpen
              ? 'opacity-100 visible translate-y-0'
              : 'opacity-0 invisible -translate-y-1'
          }`}
        >
          <div className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl shadow-xl py-2 overflow-hidden">
            {Object.entries(groups).map(([groupKey, children], gi) => (
              <div key={groupKey}>
                {gi > 0 && <div className="mx-3 my-1 border-t border-slate-100 dark:border-slate-700" />}
                <div className="px-4 py-1.5 text-[11px] font-semibold uppercase tracking-wider text-slate-400 dark:text-slate-500">
                  {GROUP_LABELS[groupKey] ?? groupKey}
                </div>
                {children.map((child) => {
                  const childActiveFlag = isActive(child.path, currentPath)
                  return (
                    <Link
                      key={child.path + child.labelKey}
                      to={child.path}
                      className={`flex items-center gap-2 px-4 py-2 text-sm transition-all duration-150 ${
                        childActiveFlag
                          ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                          : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 hover:pl-5'
                      }`}
                    >
                      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${childActiveFlag ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'}`} />
                      <span>{t(child.labelKey)}</span>
                    </Link>
                  )
                })}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// ── Navbar ────────────────────────────────────────────────────

export default function Navbar() {
  const { t } = useTranslation()
  const location = useLocation()
  const [dark, toggleTheme] = useTheme()
  const [menuOpen, setMenuOpen] = useState(false)
  const [mobileExpanded, setMobileExpanded] = useState<Set<string>>(new Set())
  const mobileRef = useRef<HTMLDivElement>(null)
  const visible = useScrollHide()
  const scrollProgress = useScrollProgress()

  useEffect(() => {
    setMenuOpen(false)
    setMobileExpanded(new Set())
  }, [location.pathname])

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (mobileRef.current && !mobileRef.current.contains(e.target as Node)) setMenuOpen(false)
    }
    if (menuOpen) {
      document.addEventListener('mousedown', handleClick)
      return () => document.removeEventListener('mousedown', handleClick)
    }
  }, [menuOpen])

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setMenuOpen(false)
    }
    if (menuOpen) {
      document.addEventListener('keydown', handleEscape)
      return () => document.removeEventListener('keydown', handleEscape)
    }
  }, [menuOpen])

  const toggleMobileSub = (labelKey: string) => {
    setMobileExpanded((prev) => {
      const next = new Set(prev)
      if (next.has(labelKey)) next.delete(labelKey)
      else next.add(labelKey)
      return next
    })
  }

  return (
    <header
      className={`border-b border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 sticky top-0 z-50 transition-all duration-300 ${
        visible ? 'translate-y-0' : '-translate-y-full'
      }`}
    >
      {/* Scroll progress bar */}
      <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-slate-200 dark:bg-slate-800">
        <div
          className="h-full bg-blue-600 dark:bg-blue-400 transition-all duration-150 ease-out"
          style={{ width: `${scrollProgress * 100}%` }}
        />
      </div>

      <nav className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 text-xl font-bold tracking-tight group">
          <span className="bg-gradient-to-br from-amber-400 to-orange-500 text-white text-lg w-8 h-8 rounded-lg flex items-center justify-center shadow-sm group-hover:shadow-md transition-shadow duration-200">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </span>
          <span className="text-slate-800 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors duration-200">
            {t('brand')}
          </span>
        </Link>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-0.5">
          {NAV_ITEMS.map((item) => (
            <DesktopNavItem
              key={item.labelKey}
              item={item}
              currentPath={location.pathname}
              isDisabled={!!item.disabled}
            />
          ))}
        </div>

        {/* Right side */}
        <div className="flex items-center gap-0.5">
          <LanguageSwitcher />

          <button
            onClick={toggleTheme}
            aria-label={t('theme.dark')}
            className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
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
            className="md:hidden p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:text-slate-700 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800 transition-all duration-200"
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

      {/* Mobile nav */}
      <div
        className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${
          menuOpen ? 'max-h-[80vh] opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div ref={mobileRef} className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="px-3 py-3 space-y-1 max-h-[70vh] overflow-y-auto">
            {NAV_ITEMS.map((item) => {
              const active = !item.disabled && (isActive(item.path, location.pathname) || childActive(item.children, location.pathname))
              const expanded = mobileExpanded.has(item.labelKey)
              const hasChildren = !!item.children

              if (item.disabled) {
                return (
                  <div key={item.labelKey} className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium text-slate-400 dark:text-slate-600 opacity-50 cursor-default">
                    <span className="shrink-0 text-lg">{item.icon}</span>
                    <span>{t(item.labelKey)}</span>
                    <span className="ml-auto text-[10px] uppercase tracking-wider">Soon</span>
                  </div>
                )
              }

              return (
                <div key={item.labelKey}>
                  {hasChildren ? (
                    <button
                      onClick={() => toggleMobileSub(item.labelKey)}
                      className={`w-full flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        active
                          ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                          : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                      }`}
                    >
                      <span className="flex items-center gap-2">
                        <span className="shrink-0 text-lg">{item.icon}</span>
                        <span>{t(item.labelKey)}</span>
                      </span>
                      <svg
                        className={`w-3.5 h-3.5 transition-transform duration-200 ${expanded ? 'rotate-180' : ''}`}
                        fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}
                      >
                        <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                      </svg>
                    </button>
                  ) : (
                    <Link
                      to={item.path ?? '#'}
                      className={`flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                        active
                          ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                          : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                      }`}
                    >
                      <span className="shrink-0 text-lg">{item.icon}</span>
                      <span>{t(item.labelKey)}</span>
                    </Link>
                  )}

                  {hasChildren && expanded && (
                    <div className="ml-6 mt-1 mb-1 space-y-0.5 border-l-2 border-slate-200 dark:border-slate-700 pl-3 overflow-hidden">
                      {item.children!.map((child) => {
                        const childActiveFlag = isActive(child.path, location.pathname)
                        return (
                          <Link
                            key={child.path + child.labelKey}
                            to={child.path}
                            className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                              childActiveFlag
                                ? 'bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium'
                                : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
                            }`}
                          >
                            <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${childActiveFlag ? 'bg-blue-500' : 'bg-slate-300 dark:bg-slate-600'}`} />
                            <span>{t(child.labelKey)}</span>
                          </Link>
                        )
                      })}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </header>
  )
}
