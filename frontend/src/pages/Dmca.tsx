import Seo from '../components/Seo.tsx'
import AdUnit from '../components/AdUnit.tsx'
import { ADS } from '../ads.ts'

export default function Dmca() {
  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <Seo
        title="DMCA - InstaDownload"
        description="InstaDownload respects intellectual property rights. Submit DMCA takedown requests here."
        path="/dmca"
      />

      <AdUnit className="max-w-2xl mx-auto mb-6" slot={ADS.BANNER_TOP} />

      <h1 className="text-3xl font-bold">DMCA Notice & Takedown</h1>
      <p className="text-sm text-slate-500 dark:text-slate-400">Last updated: May 2026</p>

      <section className="space-y-4 text-slate-700 dark:text-slate-300 leading-relaxed">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Copyright Compliance</h2>
        <p>
          InstaDownload respects the intellectual property rights of others. We comply with the
          Digital Millennium Copyright Act (DMCA) and respond to valid takedown notices.
        </p>
        <p>
          InstaDownload is a tool that retrieves publicly available media at the user's request.
          We do not host, upload, or cache content on our servers beyond temporary processing
          (files are automatically deleted within 30 minutes).
        </p>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Submitting a DMCA Notice</h2>
        <p>
          If you believe content accessible through our service infringes your copyright, please
          provide the following information:
        </p>
        <ul className="list-disc pl-6 space-y-1">
          <li>A physical or electronic signature of the copyright owner or authorized agent.</li>
          <li>Identification of the copyrighted work claimed to have been infringed.</li>
          <li>The URL or identifier of the material you claim is infringing.</li>
          <li>Your contact information (email address, phone number, and mailing address).</li>
          <li>A statement that you have a good faith belief the use is not authorized.</li>
          <li>A statement, under penalty of perjury, that the information is accurate and you are authorized to act.</li>
        </ul>
      </section>

      <AdUnit className="max-w-2xl mx-auto" slot={ADS.IN_CONTENT_2} />

      <section className="space-y-4 text-slate-700 dark:text-slate-300 leading-relaxed">
        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Send Notices To</h2>
        <div className="bg-slate-100 dark:bg-slate-800 rounded-xl p-5 space-y-1">
          <p><strong>Email:</strong> dmca@instadownload.app</p>
          <p><strong>Response Time:</strong> We aim to respond within 48 hours.</p>
        </div>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-white">Counter-Notice</h2>
        <p>
          If you believe material was removed in error, you may submit a counter-notice with:
          your contact information, identification of the removed material, a statement under
          penalty of perjury that you have a good faith belief the material was removed by mistake,
          and your consent to jurisdiction in your local federal district court.
        </p>
      </section>

      <AdUnit className="max-w-2xl mx-auto mt-8" slot={ADS.BANNER_BOTTOM} />
    </div>
  )
}
