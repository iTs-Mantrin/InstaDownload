import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero */}
      <section className="text-center py-16 space-y-6">
        <h1 className="text-5xl md:text-6xl font-bold tracking-tight">
          Download from{' '}
          <span className="text-red-500">YouTube</span>{' '}
          <span className="text-pink-500">&amp;</span>{' '}
          <span className="text-purple-400">Instagram</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-xl mx-auto">
          Fast, free, and private. Paste a link and download in seconds. No account needed.
        </p>
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

      {/* Features */}
      <section className="grid md:grid-cols-3 gap-6">
        {[
          { title: 'High Quality', desc: 'Download up to 4K resolution. Choose your preferred format and quality.' },
          { title: 'Audio Only', desc: 'Extract MP3 audio from any YouTube video at 192kbps.' },
          { title: 'Fast & Free', desc: 'Powered by yt-dlp. No limits, no sign-ups, no tracking.' },
        ].map((f) => (
          <div key={f.title} className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
            <h3 className="text-lg font-semibold mb-2">{f.title}</h3>
            <p className="text-sm text-slate-400">{f.desc}</p>
          </div>
        ))}
      </section>
    </div>
  )
}
