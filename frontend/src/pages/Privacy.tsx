import Seo from '../components/Seo.tsx'

export default function Privacy() {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <Seo
        title="Privacy Policy - InstaDownload"
        description="InstaDownload respects your privacy. Read our privacy policy to understand how we handle your data."
        path="/privacy"
      />

      <h1 className="text-3xl font-bold">Privacy Policy</h1>
      <p className="text-sm text-slate-500 dark:text-slate-400">Last updated: May 2026</p>

      <section className="space-y-4 text-slate-700 dark:text-slate-300 leading-relaxed">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">1. Information We Collect</h2>
        <p>
          InstaDownload does not require an account or registration. We do not collect any personal
          information beyond what is necessary to provide the service:
        </p>
        <ul className="list-disc pl-6 space-y-1">
          <li><strong>URLs you submit</strong> — processed temporarily to fetch media and immediately discarded.</li>
          <li><strong>Anonymous usage data</strong> — page views, download counts (no IP or user identifiers stored long-term).</li>
          <li><strong>Cookies</strong> — only for theme preference (dark/light mode). No tracking or advertising cookies are set by us.</li>
        </ul>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">2. How We Use Data</h2>
        <p>
          The URLs you provide are used solely to retrieve the requested media from YouTube or Instagram.
          We do not store, share, or re-distribute submitted URLs. Downloaded files are automatically
          deleted from our servers within 30 minutes.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">3. Third-Party Services</h2>
        <p>
          We display ads via Google AdSense. Google may use cookies to serve personalized ads based on
          your browsing history. You can opt out of personalized advertising by visiting
          {' '}<a href="https://adssettings.google.com" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">Google Ad Settings</a>.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">4. Data Security</h2>
        <p>
          All communication with our servers is encrypted via HTTPS. We implement rate limiting and
          input validation to protect against abuse. No user data is sold, traded, or transferred to third parties.
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">5. Contact</h2>
        <p>
          If you have questions about this privacy policy, please{' '}
          <a href="/contact" className="text-blue-600 hover:underline">contact us</a>.
        </p>
      </section>
    </div>
  )
}
