export type GroupRequest = {
  adults: number
  children: number
  seniors: number
}

export type TripPlanRequest = {
  origin: string
  destination: string
  travel_date: string
  departure_preference: string
  return_time_preference?: string | null
  trip_end_time_preference?: string | null
  group: GroupRequest
  preferences?: string[]
}

export type PlannerEvent =
  | { type: 'status'; message: string; cache_hit?: boolean }
  | { type: 'context'; weather?: WeatherContext }
  | { type: 'complete'; itinerary: Itinerary }
  | { type: 'error'; message: string }

export type Coordinates = {
  name?: string
  lat?: number
  lng?: number
  resolved_name?: string
  text?: string
  coordinates?: Record<string, unknown>
}

export type WeatherContext = {
  origin?: Record<string, unknown>
  destination?: Record<string, unknown>
}

export type Itinerary = {
  phase?: string
  status?: string
  origin?: Coordinates
  destination?: Coordinates
  travel_date?: string
  departure_preference?: string
  group?: GroupRequest
  distance_km?: number
  legs?: Array<Record<string, unknown>>
  total_duration_minutes?: number
  total_cost_inr?: Record<string, number>
  contextual_data?: {
    weather?: Record<string, unknown>
    temple?: Record<string, unknown>[]
    hotels?: Record<string, unknown>[]
    budget_summary?: Record<string, unknown>
  }
  transport_options?: {
    trains?: Record<string, unknown>[]
    buses?: Record<string, unknown>[]
  }
  context?: {
    weather?: WeatherContext
    temples?: Record<string, unknown>[]
    hotels?: Record<string, unknown>[]
  }
  confidence_summary?: {
    overall?: string
    low_confidence_legs?: string[]
    warnings?: string[]
  }
  confidence?: {
    overall?: string
    note?: string
  }
}

export type SavedItinerary = {
  id: string
  savedAt: string
  request: TripPlanRequest
  itinerary: Itinerary
}
