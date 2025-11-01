"""Pydantic schemas for the Scottish Landmarks application."""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class LandmarkCategory(str, Enum):
    """Categories of Scottish landmarks."""

    CASTLE = "castle"
    MOUNTAIN = "mountain"
    LOCH = "loch"
    HISTORIC_SITE = "historic_site"
    NATURAL_WONDER = "natural_wonder"
    CITY = "city"
    ISLAND = "island"


class PhotoLink(BaseModel):
    """Link to a photo of a location."""

    url: str
    source: str = Field(default="unknown")
    title: Optional[str] = None


class ReviewLink(BaseModel):
    """Link to reviews of a location."""

    url: str
    source: str = Field(default="unknown")
    rating: Optional[float] = Field(None, ge=0, le=5)


class Hotspot(BaseModel):
    """A hotspot or point of interest within a location."""

    name: str
    description: str
    why_visit: str


class LocationDescription(BaseModel):
    """Detailed description of a Scottish landmark."""

    landmark_name: str
    category: LandmarkCategory
    description: str
    photo_links: list[PhotoLink] = Field(default_factory=list)
    review_links: list[ReviewLink] = Field(default_factory=list)
    hotspots: list[Hotspot] = Field(default_factory=list)
    best_time_to_visit: str
    estimated_duration: str = Field(default="2-3 hours")


class TravelPlanRequest(BaseModel):
    """Request for a travel plan."""

    days_available: int = Field(..., ge=1, le=14)
    interests: list[LandmarkCategory] = Field(..., min_items=1)
    start_location: str = Field(default="Edinburgh")
    budget: Optional[str] = None


class Itinerary(BaseModel):
    """Day-by-day itinerary item."""

    day: int
    locations: list[LocationDescription]
    notes: str


class TravelPlan(BaseModel):
    """Complete travel plan."""

    title: str
    summary: str
    itinerary: list[Itinerary]
    total_distance_km: float
    estimated_cost: Optional[str] = None
