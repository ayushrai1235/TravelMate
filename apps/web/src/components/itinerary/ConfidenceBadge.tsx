import { CheckCircle2, HelpCircle, ShieldAlert } from 'lucide-react'

type ConfidenceBadgeProps = {
  value?: string
}

export function ConfidenceBadge({ value = 'PENDING' }: ConfidenceBadgeProps) {
  const level = value.toUpperCase()
  const tone =
    level === 'HIGH'
      ? 'border-emerald-200 bg-emerald-50 text-emerald-800 dark:border-emerald-900/60 dark:bg-emerald-950/30 dark:text-emerald-200'
      : level === 'MEDIUM'
        ? 'border-amber-200 bg-amber-50 text-amber-800 dark:border-amber-900/60 dark:bg-amber-950/30 dark:text-amber-200'
        : 'border-slate-200 bg-slate-50 text-slate-700 dark:border-slate-800 dark:bg-slate-900 dark:text-slate-200'
  const Icon = level === 'HIGH' ? CheckCircle2 : level === 'MEDIUM' ? HelpCircle : ShieldAlert

  return (
    <span className={`inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs font-semibold ${tone}`}>
      <Icon className="size-3.5" aria-hidden="true" />
      {level}
    </span>
  )
}
