import YouTubeDownloader from '../components/YouTubeDownloader.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'

export default function YouTubePage() {
  return (
    <div className="space-y-6">
      <AdUnit className="mb-6" slot={ADS.BANNER_TOP} />

      <div className="max-w-xl mx-auto">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold">YouTube Downloader</h1>
          <p className="text-slate-500 dark:text-slate-400 mt-1">Download videos or extract audio</p>
        </div>

        <YouTubeDownloader />
      </div>

      <AdUnit className="max-w-3xl mx-auto" slot={ADS.IN_CONTENT} />

      <AdUnit className="max-w-3xl mx-auto mt-8" slot={ADS.BANNER_BOTTOM} />
    </div>
  )
}
