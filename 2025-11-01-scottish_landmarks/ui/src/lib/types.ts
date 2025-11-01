// TypeScript interfaces matching the backend schemas

export type LandmarkCategory = 'castle' | 'mountain' | 'loch' | 'historic_site' | 'natural_wonder' | 'city' | 'island';

export interface PhotoLink {
  url: string;
  source: string;
  title?: string;
}

export interface ReviewLink {
  url: string;
  source: string;
  rating?: number;
}

export interface Hotspot {
  name: string;
  description: string;
  why_visit: string;
}

export interface LocationDescription {
  landmark_name: string;
  category: LandmarkCategory;
  description: string;
  photo_links: PhotoLink[];
  review_links: ReviewLink[];
  hotspots: Hotspot[];
  best_time_to_visit: string;
  estimated_duration: string;
}

export interface TravelPlanRequest {
  days_available: number;
  interests: LandmarkCategory[];
  start_location: string;
  budget?: string;
}

export interface Itinerary {
  day: number;
  locations: LocationDescription[];
  notes: string;
}

export interface TravelPlan {
  title: string;
  summary: string;
  itinerary: Itinerary[];
  total_distance_km: number;
  estimated_cost?: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'status' | 'step' | 'result' | 'error';
  message?: string;
  step?: string;
  progress?: number;
  data?: TravelPlan;
}
