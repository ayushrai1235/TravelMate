'use client'

import { useEffect, useRef, useState } from 'react'
import mapboxgl from 'mapbox-gl'
import type { Itinerary } from '@/types/trip'

type TripMapProps = {
  itinerary?: Itinerary
}

export function TripMap({ itinerary }: TripMapProps) {
  const mapRef = useRef<HTMLDivElement | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const token = process.env.NEXT_PUBLIC_MAPBOX_TOKEN

  // Extract coordinates from backend itinerary - try multiple paths
  const originCoords = (() => {
    if (!itinerary) return null
    // Backend sends: origin.coordinates with lat/lng
    const coords = itinerary.origin?.coordinates as Record<string, number> | undefined
    if (coords?.lat && coords?.lng) return { lat: coords.lat, lng: coords.lng }
    // Or directly on origin
    if (itinerary.origin?.lat && itinerary.origin?.lng) return { lat: itinerary.origin.lat, lng: itinerary.origin.lng }
    return null
  })()

  const destCoords = (() => {
    if (!itinerary) return null
    const coords = itinerary.destination?.coordinates as Record<string, number> | undefined
    if (coords?.lat && coords?.lng) return { lat: coords.lat, lng: coords.lng }
    if (itinerary.destination?.lat && itinerary.destination?.lng) return { lat: itinerary.destination.lat, lng: itinerary.destination.lng }
    return null
  })()

  const origin = itinerary?.origin
  const destination = itinerary?.destination
  const hasCoordinates =
    originCoords && destCoords

  useEffect(() => {
    if (!token || !hasCoordinates || !mapRef.current || !originCoords || !destCoords) return

    mapboxgl.accessToken = token
    const bounds = new mapboxgl.LngLatBounds(
      [originCoords.lng, originCoords.lat],
      [destCoords.lng, destCoords.lat]
    )

    const map = new mapboxgl.Map({
      container: mapRef.current,
      style: 'mapbox://styles/mapbox/streets-v12',
      bounds,
      fitBoundsOptions: { padding: 64 },
    })

    map.on('load', () => {
      new mapboxgl.Marker({ color: '#059669' }).setLngLat([originCoords.lng, originCoords.lat]).addTo(map)
      new mapboxgl.Marker({ color: '#dc2626' }).setLngLat([destCoords.lng, destCoords.lat]).addTo(map)
      map.addSource('route', {
        type: 'geojson',
        data: {
          type: 'Feature',
          properties: {},
          geometry: {
            type: 'LineString',
            coordinates: [
              [originCoords.lng, originCoords.lat],
              [destCoords.lng, destCoords.lat],
            ],
          },
        },
      })
      map.addLayer({
        id: 'route',
        type: 'line',
        source: 'route',
        paint: {
          'line-color': '#0f766e',
          'line-width': 4,
          'line-dasharray': [2, 2],
        },
      })
    })
    map.on('error', () => setMapError('Map could not load. Check the Mapbox token and network.'))

    return () => map.remove()
  }, [destCoords, hasCoordinates, origin, originCoords, token])

  if (!token || !hasCoordinates) {
    return (
      <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
        <h2 className="sm font-semibold text-slate-950 dark:text-white">Route Map</h2>
        <div className="mt-4 grid min-h-64 place-items-center rounded-md bg-[linear-gradient(90deg,#e2e8f0_1px,transparent_1px),linear-gradient(#e2e8f0_1px,transparent_1px)] bg-[size:28px_28px] p-6 text-center dark:bg-[linear-gradient(90deg,#1e293b_1px,transparent_1px),linear-gradient(#1e293b_1px,transparent_1px)]">
          <div>
            <p className="text-sm font-medium text-slate-800 dark:text-slate-100">
              {origin?.resolved_name ?? origin?.text ?? origin?.name ?? 'Origin'} to {destination?.resolved_name ?? destination?.text ?? destination?.name ?? 'Destination'}
            </p>
            <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
              {token ? 'Map coordinates not available yet. Try planning a trip first.' : 'Add NEXT_PUBLIC_MAPBOX_TOKEN to enable Mapbox rendering.'}
            </p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-800 dark:bg-slate-950">
      <h2 className="text-sm font-semibold text-slate-950 dark:text-white">Route Map</h2>
      <div ref={mapRef} className="mt-4 h-80 overflow-hidden rounded-md" />
      {mapError ? <p className="mt-2 text-sm text-red-600">{mapError}</p> : null}
    </section>
  )
}
