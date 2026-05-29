import Seo from '../components/Seo.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'

export default function Terms() {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <Seo
        title="Terms of Service - InstaDownload"
        description="Read the terms of service for using InstaDownload's media downloader tools."
        path="/terms"
      />

      <AdUnit className="max-w-2xl mx-auto mb-6" slot={ADS.BANNER_TOP} />

      <h1 className="text-3xl font-bold">Terms of Service</h1>
      <p className="text-sm text-slate-500 dark:text-slate-400">Last updated: May 2026</p>

      <section className="space-y-4 text-slate-700 dark:text-slate-300 leading-relaxed">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">1. Acceptance of Terms</h2>
        <p>
          By accessing or using InstaDownload, you agree to be bound by these Terms of Service.
          If you do not agree, please do not use our service.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">2. Description of Service</h2>
        <p>
          InstaDownload provides a free tool to download publicly available media from YouTube and
          Instagram. We do not host, upload, or distribute content. All media is fetched from the
          respective platforms at the user's request.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">3. Acceptable Use</h2>
        <p>You agree to use InstaDownload only for lawful purposes and in accordance with these terms:</p>
        <ul className="list-disc pl-6 space-y-1">
          <li>You will only download content you have the right to access.</li>
          <li>You will not use the service to infringe copyright or other intellectual property rights.</li>
          <li>You will not attempt to bypass rate limits, security measures, or automate requests excessively.</li>
          <li>You will not use the service for any illegal activity.</li>
        </ul>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">4. Intellectual Property</h2>
        <p>
          Downloaded content remains the property of its respective owners. You are responsible for
          ensuring your use of downloaded content complies with applicable copyright laws and platform terms.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">5. Limitation of Liability</h2>
        <p>
          InstaDownload is provided "as is" without warranties of any kind. We are not responsible
          for how users utilize downloaded content. We may modify or discontinue the service at any
          time without notice.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">6. Changes to Terms</h2>
        <p>
          We reserve the right to update these terms at any time. Continued use of the service after
          changes constitutes acceptance of the new terms.
        </p>
      </section>

      <AdUnit className="max-w-2xl mx-auto mt-8" slot={ADS.BANNER_BOTTOM} />
    </div>
  )
}
