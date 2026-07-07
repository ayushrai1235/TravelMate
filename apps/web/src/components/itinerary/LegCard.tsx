import { Bus, ChevronDown, ChevronUp, TrainFront } from 'lucide-react'
import { useState } from 'react'

type LegCardProps = {
  kind: 'train' | 'bus'
  leg: Record<string, unknown>
  index: number
}

function textFrom(value: unknown, fallback: string) {
  if (value == null) return fallback
  if (typeof value === 'string' || typeof value === 'number') return String(value)
  if (typeof value === 'object') {
    if ('name' in value) return textFrom((value as any).name, fallback)
    return JSON.stringify(value)
  }
  return fallback
}

function formatCost(cost: unknown): string {
  if (typeof cost === 'object' && cost !== null) {
    const min = (cost as any).min ?? 0
    const max = (cost as any).max ?? 0
    return `₹${min.toLocaleString('en-IN')} - ₹${max.toLocaleString('en-IN')}`
  }
  return '₹0'
}

function formatDuration(minutes: unknown): string {
  if (typeof minutes !== 'number') return 'N/A'
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  if (hours > 0 && mins > 0) return `${hours}h ${mins}m`
  if (hours > 0) return `${hours}h`
  return `${mins}m`
}

export function LegCard({ kind, leg, index }: LegCardProps) {
  const [expanded, setExpanded] = useState(false)
  const Icon = kind === 'train' ? TrainFront : Bus

  const title = textFrom(
    leg.train_name ?? leg.route_name ?? leg.operator ?? leg.name,
    `${kind === 'train' ? 'Train' : 'Bus'} option ${index + 1}`
  )

  const trainNumber = textFrom(leg.train_number ?? leg.number ?? '', '')
  const departureTime = textFrom(leg.departure_time ?? leg.departure ?? '', 'N/A')
  const arrivalTime = textFrom(leg.arrival_time ?? leg.arrival ?? '', 'N/A')
  const originName = textFrom(leg.origin?.name ?? leg.origin ?? '', 'Unknown')
  const destinationName = textFrom(leg.destination?.name ?? leg.destination ?? '', 'Unknown')
  const duration = formatDuration(leg.duration_minutes ?? leg.duration ?? 0)
  const cost = formatCost(leg.cost_inr ?? leg.cost ?? 0)
  const confidence = leg.confidence ?? 'MEDIUM'

  const detailEntries = Object.entries(leg).filter(([key]) => {
    const skipKeys = ['leg_id', 'sequence', 'mode', 'origin', 'destination', 'cost_inr', 'duration_minutes', 'confidence']
    return !skipKeys.includes(key) && leg[key] !== undefined && leg[key] !== null
  })

  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 transition-shadow hover:shadow-md dark:border-slate-800 dark:bg-slate-950">
      <button
        type="button"
        className="flex w-full items-start gap-3 text-left"
        onClick={() => setExpanded(!expanded)}
      >
        <span className="flex size-9 shrink-0 items-center justify-center rounded-md bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-200">
          <Icon className="size-4" aria-hidden="true" />
        </span>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate text-sm font-semibold text-slate-950 dark:text-white">{title}</h3>
            {trainNumber && <span className="shrink-0 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-medium text-slate-600 dark:bg-slate-800 dark:text-slate-400">{trainNumber}</span>}
          </div>
          <div className="mt-0.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-slate-600 dark:text-slate-400">
            <span className="truncate">{departureTime} {originName}</span>
            <span className="text-slate-400">→</span>
            <span className="truncate">{arrivalTime} {destinationName}</span>
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
            <span className="rounded bg-slate-50 px-2 py-1 dark:bg-slate-900">{duration}</span>
            <span className="rounded bg-emerald-50 px-2 py-1 font-medium text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">{cost}</span>
            <span className={`rounded px-2 py-1 font-medium ${confidence === 'HIGH' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300' : confidence === 'MEDIUM' ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/30 dark:text-amber-300' : 'bg-red-50 text-red-700 dark:bg-red-950/30 dark:text-red-300'}`}>{confidence}</span>
          </div>
        </div>
        {expanded ? (
          <ChevronUp className="size-4 shrink-0 text-slate-400" aria-hidden="true" />
        ) : (
          <ChevronDown className="size-4 shrink-0 text-slate-400" aria-hidden="true" />
        )}
      </button>

      {expanded && detailEntries.length > 0 && (
        <dl className="mt-4 grid grid-cols-2 gap-2 rounded-lg bg-slate-50 p-3 text-xs dark:bg-slate-900">
          {detailEntries.map(([key, value]) => (
            <div key={key} className="min-w-0">
              <dt className="truncate font-medium capitalize text-slate-500 dark:text-slate-400">{key.replaceAll('_', ' ')}</dt>
              <dd className="mt-0.5 truncate text-slate-700 dark:text-slate-300">{textFrom(value, JSON.stringify(value))}</dd>
            </div>
          ))}
        </dl>
      )}
    </article>
  )
}
