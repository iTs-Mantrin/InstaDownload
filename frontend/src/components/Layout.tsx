import { type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import AdUnit from './AdUnit.tsx'
import { ADS } from '../ads.ts'

export default function Layout({ children }: { children: ReactNode }) {
  const { t } = useTranslation()

  return (
    <div className="min-h-screen flex flex-col bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100 transition-colors duration-300">
      {/* Main content */}
      <main className="flex-1 max-w-6xl mx-auto w-full px-4 py-8">
        {children}
      </main>

      {/* Footer ad */}
      <div className="max-w-6xl mx-auto px-4 py-4">
        <AdUnit slot={ADS.FOOTER} />
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-200 dark:border-slate-800 pt-12 pb-8 text-sm text-slate-500 dark:text-slate-500 transition-colors duration-300">
        <div className="max-w-6xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-8 mb-10">
            {/* Brand */}
            <div className="col-span-2 md:col-span-1">
              <Link to="/" className="text-lg font-bold tracking-tight text-amber-500 dark:text-amber-400">
                {t('brand')}
              </Link>
              <p className="mt-2 text-xs leading-relaxed text-slate-400 dark:text-slate-500">
                {t('footer.brandDescription')}
              </p>
            </div>

            {/* Tools */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3 text-sm">{t('footer.tools')}</h3>
              <ul className="space-y-2">
                <li><Link to="/youtube" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.toolsList.youtubeDownloader')}</Link></li>
                <li><Link to="/youtube-mp3" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.toolsList.youtubeMp3')}</Link></li>
                <li><Link to="/instagram" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.toolsList.instagramDownloader')}</Link></li>
                <li><Link to="/instagram-story" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.toolsList.instagramStory')}</Link></li>
              </ul>
            </div>

            {/* YouTube Guides */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3 text-sm">{t('footer.youtubeGuides')}</h3>
              <ul className="space-y-2">
                <li><Link to="/youtube" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.youtubeGuidesList.downloadVideos')}</Link></li>
                <li><Link to="/youtube-mp3" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.youtubeGuidesList.convertMp3')}</Link></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.youtubeGuidesList.download4k')}</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.youtubeGuidesList.shorts')}</span></li>
              </ul>
            </div>

            {/* Instagram Guides */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3 text-sm">{t('footer.instagramGuides')}</h3>
              <ul className="space-y-2">
                <li><Link to="/instagram" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.instagramGuidesList.downloadPosts')}</Link></li>
                <li><Link to="/instagram-story" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.instagramGuidesList.downloadStories')}</Link></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.instagramGuidesList.profilePics')}</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.instagramGuidesList.igtv')}</span></li>
              </ul>
            </div>

            {/* More Platforms */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3 text-sm">{t('footer.morePlatforms')}</h3>
              <ul className="space-y-2">
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.morePlatformsList.facebook')}</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.morePlatformsList.tiktok')}</span></li>
                <li><span className="text-slate-400 dark:text-slate-600 cursor-default">{t('footer.morePlatformsList.pinterest')}</span></li>
              </ul>
            </div>

            {/* Legal & Support */}
            <div>
              <h3 className="font-semibold text-slate-700 dark:text-slate-300 mb-3 text-sm">{t('footer.legal')}</h3>
              <ul className="space-y-2">
                <li><Link to="/privacy" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.legalList.privacy')}</Link></li>
                <li><Link to="/terms" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.legalList.terms')}</Link></li>
                <li><Link to="/dmca" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.legalList.dmca')}</Link></li>
                <li className="mt-3"><Link to="/contact" className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors duration-150">{t('footer.legalList.contact')}</Link></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-slate-200 dark:border-slate-800 pt-6 text-center text-xs text-slate-400 dark:text-slate-600">
            <p>&copy; {new Date().getFullYear()} {t('brand')}. {t('footer.copyright')}</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
