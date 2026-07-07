import { Bus, CircleDot, MapPin, Sparkles, TrainFront, Footprints } from 'lucide-react'
import type { Itinerary } from '@/types/trip'

type TripTimelineProps = {
  itinerary?: Itinerary
  statuses: string[]
}

function getLabel(origin: any): string {
  return origin?.resolved_name ?? origin?.text ?? origin?.name ?? 'Unknown'
}

function formatDuration(minutes: number | undefined): string {
  if (!minutes) return 'N/A'
  const hours = Math.floor(minutes / 60)
  const mins = Math.round(minutes % 60)
  if (hours > 0 && mins > 0) return `${hours}h ${mins}m`
  if (hours > 0) return `${hours}h`
  return `${mins}m`
}

export function ItineraryTimeline({ itinerary, statuses }: TripTimelineProps) {
  const items: Array<{ label: string; icon: any; sublabel?: string }> = [
    { label: getLabel(itinerary?.origin), icon: CircleDot, sublabel: itinerary?.origin?.resolved_name || '' },
    ...statuses.map((status) => ({ label: status, icon: Sparkles })),
  ]

  // Add transport legs to timeline
  if (itinerary?.legs) {
    for (const leg of itinerary.legs) {
      if (leg.mode === 'TRAIN') {
        items.push({
          label: `Train: ${leg.train_name ?? leg.train_number ?? 'Train'}`,
          icon: TrainFront,
          sublabel: `${leg.departure_time ?? ''} → ${leg.arrival_time ?? ''}`,
        })
      } else if (leg.mode === 'BUS') {
        items.push({
          label: `Bus: ${leg.origin?.name ?? 'Bus'} → ${leg.destination?.name ?? ''}`,
          icon: Bus,
          sublabel: `Duration: ${formatDuration(leg.duration_minutes)}`,
        })
      } else if (leg.mode === 'AUTO') {
        items.push({
          label: `Auto: ${leg.origin?.name ?? 'Pickup'} → ${leg.destination?.name ?? 'Dropoff'}`,
          icon: Walk,
          sublabel: `Duration: ${formatDuration(leg.duration_minutes)}`,
        })
      }
    }
  }

  items.push({ label: getLabel(itinerary?.destination), icon: MapPin, sublabel: itinerary?.destination?.resolved_name || '' })

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
      <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Timeline</h2>
      <ol className="mt-4 space-y-3">
        {items.map((item, index) => {
          const Icon = item.icon
          return (
            <li key={`${item.label}-${index}`} className="flex gap-3">
              <span className="flex size-7 shrink-0 items-center justify-center rounded-full bg-slate-100 text-slate-700 dark:bg-slate-900 dark:text-slate-200">
                <Icon className="size-3.5" aria-hidden="true" />
              </span>
              <div className="min-w-0 pt-1">
                <span className="text-sm font-medium text-slate-900 dark:text-slate-100">{item.label}</span>
                {item.sublabel && <p className="text-xs text-slate-500 dark:text-slate-400">{item.sublabel}</p>}
              </div>
            </li>
          )
        })}
      </ol>
    </section>
  )
}
