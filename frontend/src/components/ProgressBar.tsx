import type { ProgressState } from '../api/client.ts'

interface ProgressBarProps {
  progress: ProgressState | null
}

export default function ProgressBar({ progress }: ProgressBarProps) {
  if (!progress || progress.status === 'idle') return null

  const isActive = progress.status === 'downloading' || progress.status === 'processing'
  const isDone = progress.status === 'done'
  const isError = progress.status === 'error'
  const isCancelled = progress.status === 'cancelled'

  const barClass = isDone
    ? 'bg-green-500'
    : isError || isCancelled
      ? 'bg-red-500'
      : 'progress-shimmer'

  return (
    <div className="mt-6 space-y-2">
      <div className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden transition-colors">
        <div
          className={`h-full rounded-full transition-all duration-300 ${barClass}`}
          style={{ width: `${Math.min(progress.percent, 100)}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-slate-500 dark:text-slate-400">
        <span>{Math.round(progress.percent)}%</span>
        {progress.speed && <span>{progress.speed}</span>}
        {progress.eta && <span>ETA: {progress.eta}</span>}
      </div>

      <div className="text-sm">
        {isActive && <span className="text-blue-600 dark:text-blue-400">Downloading{progress.filename ? `: ${progress.filename}` : ''}...</span>}
        {isDone && <span className="text-green-600 dark:text-green-400">Download complete!</span>}
        {isError && <span className="text-red-600 dark:text-red-400">Error: {progress.error_msg || 'Unknown error'}</span>}
        {isCancelled && <span className="text-yellow-600 dark:text-yellow-400">Cancelled</span>}
      </div>
    </div>
  )
}
