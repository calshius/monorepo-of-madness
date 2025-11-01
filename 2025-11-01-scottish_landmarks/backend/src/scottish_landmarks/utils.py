"""Utility functions and tools for the travel planner."""
import json
import re
from typing import Optional

import httpx
from langchain_google_genai import GoogleGenerativeAI

from scottish_landmarks.config import settings
from scottish_landmarks.schemas import (
    Hotspot,
    LandmarkCategory,
    LocationDescription,
    PhotoLink,
    ReviewLink,
)

# Scottish landmarks database
SCOTTISH_LANDMARKS = {
    "Edinburgh Castle": {
        "category": LandmarkCategory.CASTLE,
        "description": "Historic royal residence in Edinburgh",
        "location": (55.9486, -3.1977),
    },
    "Loch Ness": {
        "category": LandmarkCategory.LOCH,
        "description": "Famous deep loch in the Scottish Highlands",
        "location": (57.3265, -4.4304),
    },
    "Ben Nevis": {
        "category": LandmarkCategory.MOUNTAIN,
        "description": "Highest mountain in Scotland",
        "location": (56.7966, -5.0078),
    },
    "Stirling Castle": {
        "category": LandmarkCategory.CASTLE,
        "description": "Royal castle with panoramic views",
        "location": (56.1241, -3.9380),
    },
    "Isle of Skye": {
        "category": LandmarkCategory.ISLAND,
        "description": "Dramatic island with stunning landscapes",
        "location": (57.5, -6.2),
    },
    "Glencoe": {
        "category": LandmarkCategory.NATURAL_WONDER,
        "description": "Spectacular valley with dramatic mountains",
        "location": (56.6654, -5.1146),
    },
    "Glasgow": {
        "category": LandmarkCategory.CITY,
        "description": "Vibrant city with rich cultural heritage",
        "location": (55.8642, -4.2518),
    },
}


def get_llm_client() -> GoogleGenerativeAI:
    """Initialize and return the Gemini LLM client."""
    return GoogleGenerativeAI(
        model=settings.model_name,
        api_key=settings.gemini_token,
        temperature=settings.temperature,
        max_output_tokens=settings.max_tokens,
    )


def get_landmarks_by_category(category: LandmarkCategory) -> list[str]:
    """Get all landmarks of a specific category."""
    return [name for name, info in SCOTTISH_LANDMARKS.items() if info["category"] == category]


def get_all_landmarks() -> list[str]:
    """Get all available Scottish landmarks."""
    return list(SCOTTISH_LANDMARKS.keys())


async def search_google_images(query: str, num_results: int = 3) -> list[PhotoLink]:
    """
    Search Google Custom Search API for images related to a landmark.

    This tool is used by the LangGraph agent to fetch real photo links.

    Args:
        query: Search query for the landmark
        num_results: Number of results to return

    Returns:
        List of PhotoLink objects
    """
    if not settings.google_search_api_key:
        return []

    try:
        async with httpx.AsyncClient() as client:
            # Using Google Custom Search API
            params = {
                "q": query,
                "key": settings.google_search_api_key,
                "cx": settings.google_search_engine_id,
                "searchType": "image",
                "num": num_results,
            }

            response = await client.get(
                "https://www.googleapis.com/customsearch/v1", params=params, timeout=5.0
            )
            response.raise_for_status()

            data = response.json()
            photo_links = []

            for item in data.get("items", []):
                photo_links.append(
                    PhotoLink(
                        url=item.get("link", ""),
                        source=item.get("displayLink", "Google Images"),
                        title=item.get("title", ""),
                    )
                )

            return photo_links
    except Exception as e:
        print(f"Error searching images: {e}")
        return []


async def search_reviews(landmark_name: str) -> list[ReviewLink]:
    """
    Search for review links for a landmark (using mock data for now).

    Args:
        landmark_name: Name of the landmark

    Returns:
        List of ReviewLink objects
    """
    # Mock review links - can be enhanced with real API integration
    mock_reviews = [
        ReviewLink(
            url=f"https://www.tripadvisor.com/Tourism-g{hash(landmark_name)%100000}-{landmark_name.replace(' ', '_')}.html",
            source="TripAdvisor",
            rating=4.5,
        ),
        ReviewLink(
            url=f"https://www.google.com/maps/search/{landmark_name.replace(' ', '+')}/reviews",
            source="Google Maps",
            rating=4.3,
        ),
        ReviewLink(
            url=f"https://www.booking.com/attractions/{landmark_name.replace(' ', '-').lower()}",
            source="Booking.com",
            rating=4.2,
        ),
    ]

    return mock_reviews


async def generate_location_description(
    landmark_name: str, llm_client: Optional[GoogleGenerativeAI] = None
) -> LocationDescription:
    """
    Generate a detailed description of a landmark using Gemini.

    Args:
        landmark_name: Name of the landmark
        llm_client: Optional LLM client (creates new if not provided)

    Returns:
        LocationDescription with AI-generated content
    """
    if not llm_client:
        llm_client = get_llm_client()

    if landmark_name not in SCOTTISH_LANDMARKS:
        raise ValueError(f"Unknown landmark: {landmark_name}")

    landmark_info = SCOTTISH_LANDMARKS[landmark_name]
    category = landmark_info["category"]

    # Generate description using Gemini
    prompt = f"""You are a travel guide expert. Generate a detailed, engaging description for the Scottish landmark "{landmark_name}".

Include:
1. A compelling 2-3 sentence overview
2. 3-5 key hotspots or areas to explore within or near this landmark
3. Best time to visit
4. Estimated duration of visit

Format your response as JSON with these fields:
- "overview": string (2-3 sentences)
- "hotspots": array of objects with "name", "description", "why_visit"
- "best_time_to_visit": string
- "estimated_duration": string

Return ONLY valid JSON, no markdown code blocks."""

    response = llm_client.invoke(prompt)

    # Extract JSON from response if it contains markdown
    json_match = re.search(r'\{.*\}', response, re.DOTALL)
    json_str = json_match.group(0) if json_match else response

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback if parsing fails
        data = {
            "overview": response[:500],
            "hotspots": [],
            "best_time_to_visit": "Year-round",
            "estimated_duration": "2-3 hours",
        }

    # Create hotspots
    hotspots = [
        Hotspot(
            name=hs.get("name", f"Hotspot {i+1}"),
            description=hs.get("description", ""),
            why_visit=hs.get("why_visit", ""),
        )
        for i, hs in enumerate(data.get("hotspots", []))
    ]

    # Fetch photo and review links
    photo_links = await search_google_images(landmark_name, num_results=3)
    if not photo_links:
        # Fallback mock links
        photo_links = [
            PhotoLink(
                url=f"https://example.com/photos/{landmark_name.replace(' ', '_').lower()}_1.jpg",
                source="Scottish Tourism",
            ),
            PhotoLink(
                url=f"https://example.com/photos/{landmark_name.replace(' ', '_').lower()}_2.jpg",
                source="Visit Scotland",
            ),
        ]

    review_links = await search_reviews(landmark_name)

    return LocationDescription(
        landmark_name=landmark_name,
        category=category,
        description=data.get("overview", response),
        photo_links=photo_links,
        review_links=review_links,
        hotspots=hotspots,
        best_time_to_visit=data.get("best_time_to_visit", "Year-round"),
        estimated_duration=data.get("estimated_duration", "2-3 hours"),
    )
