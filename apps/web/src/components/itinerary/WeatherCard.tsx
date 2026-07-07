import { CloudSun } from 'lucide-react'

type WeatherCardProps = {
  title: string
  weather?: Record<string, unknown>
}

function readable(value: unknown) {
  if (value == null) return 'Not available'
  if (typeof value === 'string' || typeof value === 'number') return String(value)
  return JSON.stringify(value)
}

export function WeatherCard({ title, weather }: WeatherCardProps) {
  const entries = Object.entries(weather ?? {}).slice(0, 4)

  return (
    <article className="rounded-lg border border-sky-200 bg-sky-50 p-4 text-sky-950 dark:border-sky-900/60 dark:bg-sky-950/30 dark:text-sky-100">
      <div className="flex items-center gap-2">
        <CloudSun className="size-4" aria-hidden="true" />
        <h3 className="text-sm font-semibold">{title}</h3>
      </div>
      <dl className="mt-3 space-y-2 text-sm">
        {entries.length > 0 ? (
          entries.map(([key, value]) => (
            <div key={key} className="flex justify-between gap-3">
              <dt className="capitalize opacity-75">{key.replaceAll('_', ' ')}</dt>
              <dd className="truncate font-medium">{readable(value)}</dd>
            </div>
          ))
        ) : (
          <p className="text-sm opacity-75">Weather will appear when the backend returns it.</p>
        )}
      </dl>
    </article>
  )
}
