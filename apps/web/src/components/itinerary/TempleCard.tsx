import { Landmark } from 'lucide-react'

type TempleCardProps = {
  temple: Record<string, unknown>
}

function text(value: unknown, fallback: string) {
  return typeof value === 'string' || typeof value === 'number' ? String(value) : fallback
}

export function TempleCard({ temple }: TempleCardProps) {
  return (
    <article className="rounded-lg border border-violet-200 bg-violet-50 p-4 text-violet-950 dark:border-violet-900/60 dark:bg-violet-950/30 dark:text-violet-100">
      <div className="flex items-start gap-3">
        <Landmark className="mt-0.5 size-4" aria-hidden="true" />
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold">{text(temple.name, 'Temple')}</h3>
          <p className="mt-1 line-clamp-2 text-sm opacity-80">
            {text(temple.city ?? temple.description ?? temple.address, 'Destination context from the temple database.')}
          </p>
        </div>
      </div>
    </article>
  )
}
