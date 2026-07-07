import { WalletCards } from 'lucide-react'
import type { GroupRequest, Itinerary } from '@/types/trip'

type BudgetPanelProps = {
  itinerary?: Itinerary
  group: GroupRequest
}

export function BudgetPanel({ itinerary, group }: BudgetPanelProps) {
  const travelers = group.adults + group.children + group.seniors
  const distanceKm = itinerary?.distance_km ?? 120
  const transportEstimate = Math.max(500, Math.round(distanceKm * travelers * 2.4))
  const stayEstimate = Math.max(1800, travelers * 1200)
  const totalCost = itinerary?.total_cost_inr
  const actualTotalCost = totalCost ? totalCost.min + totalCost.max : transportEstimate + stayEstimate

  return (
    <aside className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-emerald-950 dark:border-emerald-900/60 dark:bg-emerald-950/30 dark:text-emerald-100">
      <div className="flex items-center gap-2">
        <WalletCards className="size-4" aria-hidden="true" />
        <h2 className="text-sm font-semibold">Budget</h2>
      </div>
      <dl className="mt-4 space-y-3 text-sm">
        <div className="flex justify-between gap-3">
          <dt>Distance</dt>
          <dd className="font-semibold">{distanceKm} km</dd>
        </div>
        <div className="flex justify-between gap-3">
          <dt>Transport estimate</dt>
          <dd className="font-semibold">₹{transportEstimate.toLocaleString('en-IN')}</dd>
        </div>
        <div className="flex justify-between gap-3">
          <dt>Stay buffer</dt>
          <dd className="font-semibold">₹{stayEstimate.toLocaleString('en-IN')}</dd>
        </div>
        {totalCost && (
          <div className="flex justify-between gap-3">
            <dt>Train fare (est.)</dt>
            <dd className="font-semibold">₹{totalCost.min?.toLocaleString('en-IN')} - ₹{totalCost.max?.toLocaleString('en-IN')}</dd>
          </div>
        )}
        <div className="border-t border-emerald-200 pt-3 dark:border-emerald-800">
          <div className="flex justify-between gap-3">
            <dt>Total guide</dt>
            <dd className="font-semibold">₹{actualTotalCost.toLocaleString('en-IN')}</dd>
          </div>
        </div>
      </dl>
    </aside>
  )
}
