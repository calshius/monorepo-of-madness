"""FastAPI routers for the travel planning API."""
from fastapi import APIRouter, HTTPException

from scottish_landmarks.agent import create_travel_planner_graph
from scottish_landmarks.schemas import TravelPlanRequest
from scottish_landmarks.utils import get_all_landmarks

router = APIRouter(prefix="/api/travel", tags=["travel"])


@router.get("/landmarks")
async def get_landmarks():
    """Get list of available Scottish landmarks."""
    return {"landmarks": get_all_landmarks()}


@router.get("/workflow")
async def get_workflow():
    """Get the travel planning workflow configuration."""
    return {
        "workflow": "scottish_landmarks_travel_planner",
        "version": "1.0",
        "nodes": ["select_landmarks", "generate_descriptions", "create_itinerary"],
        "status": "ready",
    }


@router.post("/plan")
async def create_travel_plan(request: TravelPlanRequest):
    """
    Create a travel plan for Scottish landmarks.

    Args:
        request: Travel plan request with user preferences

    Returns:
        Generated travel plan
    """
    try:
        graph = create_travel_planner_graph()

        # Initialize state
        initial_state = {
            "request": request,
            "selected_landmarks": [],
            "landmark_descriptions": {},
            "travel_plan": None,
            "current_step": "start",
        }

        # Execute the graph in a thread pool to avoid blocking
        loop = __import__("asyncio").get_event_loop()
        executor = __import__("concurrent.futures").futures.ThreadPoolExecutor(max_workers=1)
        result = await loop.run_in_executor(executor, graph.invoke, initial_state)

        if not result.get("travel_plan"):
            raise ValueError("Failed to generate travel plan")

        return result["travel_plan"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating travel plan: {str(e)}")
