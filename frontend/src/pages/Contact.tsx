import Seo from '../components/Seo.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'

export default function Contact() {
  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      <Seo
        title="Contact Us - InstaDownload"
        description="Get in touch with the InstaDownload team. We'll respond within 24 hours."
        path="/contact"
      />

      <AdUnit className="max-w-2xl mx-auto mb-6" slot={ADS.BANNER_TOP} />

      <h1 className="text-3xl font-bold">Contact Us</h1>
      <p className="text-slate-600 dark:text-slate-400">
        Have a question, suggestion, or found a bug? Fill out the form below and we'll get back to you within 24 hours.
      </p>

      <form
        onSubmit={(e) => e.preventDefault()}
        className="space-y-5"
      >
        <div>
          <label htmlFor="name" className="block text-sm font-medium mb-1">Name</label>
          <input
            id="name"
            type="text"
            className="w-full px-4 py-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            placeholder="Your name"
          />
        </div>

        <div>
          <label htmlFor="email" className="block text-sm font-medium mb-1">Email</label>
          <input
            id="email"
            type="email"
            className="w-full px-4 py-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label htmlFor="message" className="block text-sm font-medium mb-1">Message</label>
          <textarea
            id="message"
            rows={5}
            className="w-full px-4 py-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 transition-colors resize-y"
            placeholder="How can we help you?"
          />
        </div>

        <button
          type="submit"
          className="px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-semibold transition-colors"
        >
          Send Message
        </button>
      </form>

      <AdUnit className="max-w-2xl mx-auto" slot={ADS.IN_CONTENT} />

      <AdUnit className="max-w-2xl mx-auto" slot={ADS.BANNER_BOTTOM} />
    </div>
  )
}
