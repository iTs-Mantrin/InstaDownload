import { useEffect, useRef } from 'react'

interface AdUnitProps {
  className?: string
  slot: string
  format?: 'auto' | 'rectangle' | 'horizontal' | 'vertical'
}

declare global {
  interface Window {
    adsbygoogle: unknown[]
  }
}

export default function AdUnit({ className = '', slot, format = 'auto' }: AdUnitProps) {
  const pushed = useRef(false)

  useEffect(() => {
    if (pushed.current || !slot) return
    pushed.current = true
    try {
      window.adsbygoogle = window.adsbygoogle || []
      window.adsbygoogle.push({})
    } catch {
      // ad blocker or offline — silently ignore
    }
  }, [slot])

  // If no slot configured yet, render a visible placeholder
  if (!slot || slot === 'YOUR_AD_SLOT_ID') {
    return (
      <div
        className={`flex items-center justify-center border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-800/50 text-slate-400 dark:text-slate-600 text-sm font-medium ${className}`}
        style={{ minHeight: '90px' }}
      >
        <span>Ad Unit</span>
      </div>
    )
  }

  return (
    <div className={className}>
      <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client="ca-pub-2004545377931849"
        data-ad-slot={slot}
        data-ad-format={format}
        data-full-width-responsive="true"
      />
    </div>
  )
}
