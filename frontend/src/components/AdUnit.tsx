interface AdUnitProps {
  className?: string
}

export default function AdUnit({ className = '' }: AdUnitProps) {
  return (
    <div
      className={`flex items-center justify-center border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-xl bg-slate-50 dark:bg-slate-800/50 text-slate-400 dark:text-slate-600 text-sm font-medium ${className}`}
      style={{ minHeight: '90px' }}
    >
      <span>Ad Unit</span>
    </div>
  )
}
