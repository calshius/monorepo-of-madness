"""LangGraph tools for the travel planning agent."""
from typing import Any

from langchain_core.tools import tool

from scottish_landmarks.utils import search_google_images, search_reviews


@tool
async def search_landmark_photos(query: str, num_results: int = 3) -> list[dict]:
    """
    Search for photos of a Scottish landmark using Google Custom Search API.

    This tool is used by the agent to find real photo links for landmarks.

    Args:
        query: The landmark name or search query
        num_results: Number of photo results to return (default: 3)

    Returns:
        List of photo links with URLs, sources, and titles
    """
    try:
        photos = await search_google_images(query, num_results)
        return [
            {
                "url": p.url,
                "source": p.source,
                "title": p.title or query,
            }
            for p in photos
        ]
    except Exception as e:
        return [{"error": f"Failed to search photos: {str(e)}"}]


@tool
async def search_landmark_reviews(landmark_name: str) -> list[dict]:
    """
    Search for reviews and ratings of a Scottish landmark.

    This tool aggregates review links from multiple platforms including
    TripAdvisor, Google Maps, and Booking.com.

    Args:
        landmark_name: The name of the landmark

    Returns:
        List of review links with URLs, sources, and ratings
    """
    try:
        reviews = await search_reviews(landmark_name)
        return [
            {
                "url": r.url,
                "source": r.source,
                "rating": r.rating,
            }
            for r in reviews
        ]
    except Exception as e:
        return [{"error": f"Failed to search reviews: {str(e)}"}]


# Tool registry for LangGraph
TOOLS = [
    search_landmark_photos,
    search_landmark_reviews,
]


def get_tool_by_name(name: str) -> Any:
    """Get a tool by its name."""
    tool_map = {tool.name: tool for tool in TOOLS}
    return tool_map.get(name)
