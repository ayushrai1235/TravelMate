'use client'

import { FormEvent, useMemo, useState } from 'react'
import { Button } from '@/components/ui/button'
import { CalendarDays, Download, Loader2, MapPinned, Save } from 'lucide-react'
import type { Itinerary, PlannerEvent, TripPlanRequest } from '@/types/trip'
import { readSseStream } from './sse'
import { ConfidenceBadge } from '@/components/itinerary/ConfidenceBadge'
import { LegCard } from '@/components/itinerary/LegCard'
import { WeatherCard } from '@/components/itinerary/WeatherCard'
import { TempleCard } from '@/components/itinerary/TempleCard'
import { HotelCard } from '@/components/itinerary/HotelCard'
import { BudgetPanel } from '@/components/itinerary/BudgetPanel'
import { ItineraryTimeline } from '@/components/itinerary/ItineraryTimeline'
import { TripMap } from '@/components/map/TripMap'
import { ChatPanel } from '@/components/chat/ChatPanel'
import { useOfflineStorage } from '@/hooks/useOfflineStorage'
import { usePdfExport } from '@/hooks/usePdfExport'

type PlannerWorkspaceProps = {
  userEmail?: string | null
}

const preferenceOptions = ['temples', 'weather-safe', 'budget', 'family-friendly']

function todayIso() {
  return new Date().toISOString().slice(0, 10)
}

export function PlannerWorkspace({ userEmail }: PlannerWorkspaceProps) {
  const [request, setRequest] = useState<TripPlanRequest>({
    origin: '',
    destination: '',
    travel_date: todayIso(),
    departure_preference: 'morning',
    return_time_preference: null,
    trip_end_time_preference: null,
    group: { adults: 1, children: 0, seniors: 0 },
    preferences: ['temples'],
  })
  const [statuses, setStatuses] = useState<string[]>([])
  const [itinerary, setItinerary] = useState<Itinerary | undefined>()
  const [error, setError] = useState<string | null>(null)
  const [isPlanning, setIsPlanning] = useState(false)
  const { saved, saveItinerary, isSupported } = useOfflineStorage()
  const exportPdf = usePdfExport()

  const progress = useMemo(() => Math.min(100, statuses.length * 30 + (itinerary ? 10 : 0)), [itinerary, statuses])

  function updateGroup(key: keyof TripPlanRequest['group'], value: number) {
    setRequest((current) => ({
      ...current,
      group: { ...current.group, [key]: Math.max(0, value) },
    }))
  }

  function togglePreference(value: string) {
    setRequest((current) => {
      const preferences = current.preferences ?? []
      return {
        ...current,
        preferences: preferences.includes(value)
          ? preferences.filter((preference) => preference !== value)
          : [...preferences, value],
      }
    })
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setStatuses([])
    setItinerary(undefined)
    setError(null)
    setIsPlanning(true)

    try {
      const response = await fetch('/api/plan', {
        method: 'POST',
        headers: { 'content-type': 'application/json', accept: 'text/event-stream' },
        body: JSON.stringify(request),
      })

      if (!response.ok) {
        const text = await response.text()
        throw new Error(text || `Planning failed with status ${response.status}.`)
      }

      await readSseStream(response, (event: PlannerEvent) => {
        if (event.type === 'status') {
          setStatuses((current) => [...current, event.message])
        }
        if (event.type === 'complete') {
          setItinerary(event.itinerary)
          saveItinerary({
            id: crypto.randomUUID(),
            savedAt: new Date().toISOString(),
            request,
            itinerary: event.itinerary,
          }).catch(() => undefined)
        }
        if (event.type === 'error') {
          setError(event.message)
        }
      })
    } catch (planningError) {
      setError(planningError instanceof Error ? planningError.message : 'Planning failed.')
    } finally {
      setIsPlanning(false)
    }
  }

  const trainLegs = (itinerary?.legs ?? []).filter((leg: any) => leg.mode === 'TRAIN')
  const busLegs = (itinerary?.legs ?? []).filter((leg: any) => leg.mode === 'BUS')
  const temples = itinerary?.contextual_data?.temple ?? []
  const hotels = itinerary?.contextual_data?.hotels ?? []
  const weatherData = itinerary?.contextual_data?.weather

  return (
    <div className="bg-slate-50 px-4 py-6 dark:bg-slate-950 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm text-slate-500 dark:text-slate-400">{userEmail}</p>
            <h1 className="text-3xl font-bold tracking-tight text-slate-950 dark:text-white">Trip Planner</h1>
          </div>
          {itinerary ? (
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => saveItinerary({ id: crypto.randomUUID(), savedAt: new Date().toISOString(), request, itinerary })} disabled={!isSupported}>
                <Save className="size-4" aria-hidden="true" />
                Save Offline
              </Button>
              <Button onClick={() => exportPdf(request, itinerary)}>
                <Download className="size-4" aria-hidden="true" />
                PDF
              </Button>
            </div>
          ) : null}
        </div>

        <div className="grid gap-6 xl:grid-cols-[minmax(0,1fr)_24rem]">
          <div className="space-y-6">
            <form onSubmit={handleSubmit} className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
              <div className="grid gap-4 lg:grid-cols-4">
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Origin
                  <input
                    required
                    value={request.origin}
                    onChange={(event) => setRequest((current) => ({ ...current, origin: event.target.value }))}
                    placeholder="Bengaluru"
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900"
                  />
                </label>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Destination
                  <input
                    required
                    value={request.destination}
                    onChange={(event) => setRequest((current) => ({ ...current, destination: event.target.value }))}
                    placeholder="Tirupati"
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900"
                  />
                </label>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Date
                  <input
                    required
                    type="date"
                    min={todayIso()}
                    value={request.travel_date}
                    onChange={(event) => setRequest((current) => ({ ...current, travel_date: event.target.value }))}
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900"
                  />
                </label>
                <label className="block text-sm font-medium text-slate-700 dark:text-slate-200">
                  Departure
                  <select
                    value={request.departure_preference}
                    onChange={(event) => setRequest((current) => ({ ...current, departure_preference: event.target.value }))}
                    className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900"
                  >
                    <option value="early_morning">Early morning</option>
                    <option value="morning">Morning</option>
                    <option value="afternoon">Afternoon</option>
                    <option value="evening">Evening</option>
                  </select>
                </label>
              </div>

              <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_1fr]">
                <div className="grid grid-cols-3 gap-3">
                  {(['adults', 'children', 'seniors'] as const).map((key) => (
                    <label key={key} className="block text-sm font-medium capitalize text-slate-700 dark:text-slate-200">
                      {key}
                      <input
                        type="number"
                        min={key === 'adults' ? 1 : 0}
                        max={50}
                        value={request.group[key]}
                        onChange={(event) => updateGroup(key, Number(event.target.value))}
                        className="mt-1 h-10 w-full rounded-md border border-slate-300 bg-white px-3 text-sm outline-none focus:border-slate-950 focus:ring-2 focus:ring-slate-950/10 dark:border-slate-700 dark:bg-slate-900"
                      />
                    </label>
                  ))}
                </div>
                <div className="flex flex-wrap items-end gap-2">
                  {preferenceOptions.map((option) => (
                    <button
                      key={option}
                      type="button"
                      onClick={() => togglePreference(option)}
                      className={`h-10 rounded-md border px-3 text-sm font-medium transition ${
                        request.preferences?.includes(option)
                          ? 'border-slate-950 bg-slate-950 text-white dark:border-white dark:bg-white dark:text-slate-950'
                          : 'border-slate-300 bg-white text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-200'
                      }`}
                    >
                      {option.replaceAll('-', ' ')}
                    </button>
                  ))}
                </div>
              </div>

              <div className="mt-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-slate-400">
                  <CalendarDays className="size-4" aria-hidden="true" />
                  Streams live planning events from FastAPI.
                </div>
                <Button type="submit" size="lg" disabled={isPlanning}>
                  {isPlanning ? <Loader2 className="size-4 animate-spin" aria-hidden="true" /> : <MapPinned className="size-4" aria-hidden="true" />}
                  Plan Trip
                </Button>
              </div>
            </form>

            {(isPlanning || statuses.length > 0 || error) && (
              <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
                <div className="flex items-center justify-between gap-3">
                  <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Planning Progress</h2>
                  <span className="text-xs text-slate-500">{progress}%</span>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-900">
                  <div className="h-full bg-emerald-600 transition-all" style={{ width: `${progress}%` }} />
                </div>
                <ol className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-300">
                  {statuses.map((status, index) => (
                    <li key={`${status}-${index}`}>{status}</li>
                  ))}
                </ol>
                {error ? <p className="mt-3 rounded-md bg-red-50 px-3 py-2 text-sm text-red-700 dark:bg-red-950/30 dark:text-red-200">{error}</p> : null}
              </section>
            )}

            <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
              <div className="space-y-6">
                {itinerary ? (
                  <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
                    <div className="flex items-center justify-between gap-3">
                      <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Itinerary</h2>
                      <ConfidenceBadge value={itinerary.confidence_summary?.overall ?? itinerary.confidence?.overall} />
                    </div>
                    <div className="mt-3 grid grid-cols-2 gap-3 text-sm">
                      <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
                        <dt className="text-xs text-slate-500 dark:text-slate-400">Route</dt>
                        <dd className="mt-1 font-medium text-slate-900 dark:text-white">
                          {itinerary.origin?.resolved_name ?? itinerary.origin?.text ?? itinerary.origin?.name ?? 'Origin'} → {itinerary.destination?.resolved_name ?? itinerary.destination?.text ?? itinerary.destination?.name ?? 'Destination'}
                        </dd>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
                        <dt className="text-xs text-slate-500 dark:text-slate-400">Travel Date</dt>
                        <dd className="mt-1 font-medium text-slate-900 dark:text-white">{itinerary.travel_date ?? 'N/A'}</dd>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
                        <dt className="text-xs text-slate-500 dark:text-slate-400">Distance</dt>
                        <dd className="mt-1 font-medium text-slate-900 dark:text-white">{itinerary.distance_km ? `${itinerary.distance_km} km` : 'N/A'}</dd>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
                        <dt className="text-xs text-slate-500 dark:text-slate-400">Duration</dt>
                        <dd className="mt-1 font-medium text-slate-900 dark:text-white">{itinerary.total_duration_minutes ? `${Math.floor(itinerary.total_duration_minutes / 60)}h ${itinerary.total_duration_minutes % 60}m` : 'N/A'}</dd>
                      </div>
                      <div className="rounded-lg bg-emerald-50 p-3 dark:bg-emerald-950/30">
                        <dt className="text-xs text-emerald-700 dark:text-emerald-400">Est. Cost</dt>
                        <dd className="mt-1 font-semibold text-emerald-900 dark:text-emerald-200">
                          {itinerary.total_cost_inr ? `₹${itinerary.total_cost_inr.min?.toLocaleString('en-IN')} - ₹${itinerary.total_cost_inr.max?.toLocaleString('en-IN')}` : 'N/A'}
                        </dd>
                      </div>
                      <div className="rounded-lg bg-slate-50 p-3 dark:bg-slate-900">
                        <dt className="text-xs text-slate-500 dark:text-slate-400">Transport Modes</dt>
                        <dd className="mt-1 font-medium text-slate-900 dark:text-white">
                          {[
                            ...(itinerary.legs ?? []).filter((l: any) => l.mode === 'TRAIN').length > 0 ? ['Train'] : [],
                            ...(itinerary.legs ?? []).filter((l: any) => l.mode === 'BUS').length > 0 ? ['Bus'] : [],
                            ...(itinerary.legs ?? []).filter((l: any) => l.mode === 'AUTO').length > 0 ? ['Road'] : [],
                          ].join(', ') || 'N/A'}
                        </dd>
                      </div>
                    </div>
                    {itinerary.confidence_summary?.warnings?.length > 0 && (
                      <div className="mt-3 rounded-lg bg-amber-50 p-3 text-xs text-amber-800 dark:bg-amber-950/30 dark:text-amber-200">
                        {itinerary.confidence_summary.warnings.join(' ')}
                      </div>
                    )}
                  </section>
                ) : (
                  <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
                    <div className="flex items-center justify-between gap-3">
                      <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Itinerary</h2>
                    </div>
                    <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                      Your route options and context will appear here after planning.
                    </p>
                  </section>
                )}

                <TripMap itinerary={itinerary} />

                <section className="grid gap-4 md:grid-cols-2">
                  <WeatherCard title="Origin Weather" weather={weatherData?.origin} />
                  <WeatherCard title="Destination Weather" weather={weatherData?.destination} />
                </section>

                <section className="space-y-3">
                  <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Transport Options</h2>
                  <div className="grid gap-3 md:grid-cols-2">
                    {trainLegs.map((train, index) => <LegCard key={`train-${index}`} kind="train" leg={train} index={index} />)}
                    {busLegs.map((bus, index) => <LegCard key={`bus-${index}`} kind="bus" leg={bus} index={index} />)}
                    {trainLegs.length === 0 && busLegs.length === 0 ? (
                      <p className="rounded-lg border border-dashed border-slate-300 p-4 text-sm text-slate-500 dark:border-slate-700 dark:text-slate-400">
                        Transport cards appear after the planning stream completes.
                      </p>
                    ) : null}
                  </div>
                </section>

                <section className="grid gap-3 md:grid-cols-2">
                  {temples.length > 0 ? temples.map((temple, index) => <TempleCard key={`temple-${index}`} temple={temple} />) : <TempleCard temple={{ name: 'Temple context pending' }} />}
                  {hotels.length > 0 ? hotels.map((hotel, index) => <HotelCard key={`hotel-${index}`} hotel={hotel} />) : <HotelCard />}
                </section>
              </div>

              <div className="space-y-6">
                <ItineraryTimeline itinerary={itinerary} statuses={statuses} />
                <BudgetPanel itinerary={itinerary} group={request.group} />
                <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
                  <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Offline Plans</h2>
                  <div className="mt-3 space-y-2">
                    {saved.slice(0, 4).map((entry) => (
                      <button
                        key={entry.id}
                        className="w-full rounded-md bg-slate-50 p-3 text-left text-sm hover:bg-slate-100 dark:bg-slate-900 dark:hover:bg-slate-800"
                        onClick={() => {
                          setRequest(entry.request)
                          setItinerary(entry.itinerary)
                        }}
                      >
                        <span className="block font-medium text-slate-900 dark:text-white">
                          {entry.request.origin} to {entry.request.destination}
                        </span>
                        <span className="text-xs text-slate-500">{new Date(entry.savedAt).toLocaleString()}</span>
                      </button>
                    ))}
                    {saved.length === 0 ? <p className="text-sm text-slate-500">Saved itineraries will appear here.</p> : null}
                  </div>
                </section>
              </div>
            </div>
          </div>

          <ChatPanel />
        </div>
      </div>
    </div>
  )
}
