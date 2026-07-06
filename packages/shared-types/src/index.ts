export interface UserProfile {
  id: string;
  email: string;
  full_name?: string;
  avatar_url?: string;
  created_at: string;
}

export interface TripPlan {
  id: string;
  origin: string;
  destination: string;
  date: string;
  itinerary: any;
}
