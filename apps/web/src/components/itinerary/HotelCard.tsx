import { Hotel } from 'lucide-react'

type HotelCardProps = {
  hotel?: Record<string, unknown>
}

export function HotelCard({ hotel }: HotelCardProps) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
      <div className="flex items-start gap-3">
        <span className="flex size-9 items-center justify-center rounded-md bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-200">
          <Hotel className="size-4" aria-hidden="true" />
        </span>
        <div>
          <h3 className="text-sm font-semibold text-slate-950 dark:text-white">
            {typeof hotel?.name === 'string' ? hotel.name : 'Hotel suggestions pending'}
          </h3>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
            {typeof hotel?.description === 'string'
              ? hotel.description
              : 'The Phase 4 UI is ready to render hotel data once the backend HotelAgent is connected.'}
          </p>
        </div>
      </div>
    </article>
  )
}
