import type { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'

const NAV = [
  { label: 'Home', path: '/' },
  { label: 'YouTube', path: '/youtube' },
  { label: 'Instagram', path: '/instagram' },
]

export default function Layout({ children }: { children: ReactNode }) {
  const location = useLocation()

  return (
    <div className="min-h-screen flex flex-col">
      {/* Navbar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-sm sticky top-0 z-50">
        <nav className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
          <Link to="/" className="text-xl font-bold text-amber-400 tracking-tight">
            InstaDownload
          </Link>
          <div className="flex gap-1">
            {NAV.map((item) => {
              const isActive = location.pathname === item.path
              return (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-600 text-white'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                >
                  {item.label}
                </Link>
              )
            })}
          </div>
        </nav>
      </header>

      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-6 text-center text-sm text-slate-500">
        <p>&copy; {new Date().getFullYear()} InstaDownload. Built with yt-dlp.</p>
      </footer>
    </div>
  )
}
