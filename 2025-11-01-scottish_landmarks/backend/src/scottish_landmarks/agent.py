"""LangGraph state machine for the travel planning agent."""
import asyncio
from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from scottish_landmarks.schemas import (
    LocationDescription,
    TravelPlan,
    TravelPlanRequest,
    Itinerary,
)
from scottish_landmarks.utils import (
    generate_location_description,
    get_landmarks_by_category,
    get_llm_client,
)


class PlannerState(TypedDict):
    """State managed by the travel planner agent."""

    request: TravelPlanRequest
    selected_landmarks: list[str]
    landmark_descriptions: dict[str, LocationDescription]
    travel_plan: TravelPlan
    current_step: str


def select_landmarks_node(state: PlannerState) -> PlannerState:
    """
    Select appropriate landmarks based on user interests and available days.

    Args:
        state: Current planner state

    Returns:
        Updated state with selected landmarks
    """
    request = state["request"]
    selected = []

    # For each interest category, select 1-2 landmarks
    for category in request.interests:
        landmarks = get_landmarks_by_category(category)
        # Calculate how many landmarks to pick
        num_to_pick = min(2, len(landmarks), max(1, request.days_available // 2))
        selected.extend(landmarks[:num_to_pick])

    # Remove duplicates and limit to reasonable number
    selected = list(dict.fromkeys(selected))[: request.days_available + 2]

    state["selected_landmarks"] = selected
    state["current_step"] = "select_landmarks"

    return state


def generate_descriptions_node(state: PlannerState) -> PlannerState:
    """
    Generate detailed descriptions for each selected landmark.

    Args:
        state: Current planner state

    Returns:
        Updated state with landmark descriptions
    """

    async def async_generate():
        llm_client = get_llm_client()
        descriptions = {}

        for landmark in state["selected_landmarks"]:
            try:
                description = await generate_location_description(landmark, llm_client)
                descriptions[landmark] = description
            except Exception as e:
                print(f"Error generating description for {landmark}: {e}")
                continue

        return descriptions

    # Run async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    descriptions = loop.run_until_complete(async_generate())
    state["landmark_descriptions"] = descriptions
    state["current_step"] = "generate_descriptions"

    return state


def create_itinerary_node(state: PlannerState) -> PlannerState:
    """
    Create a day-by-day itinerary from the landmark descriptions.

    Args:
        state: Current planner state

    Returns:
        Updated state with travel plan
    """
    request = state["request"]
    descriptions = state["landmark_descriptions"]

    if not descriptions:
        raise ValueError("No landmark descriptions available")

    # Create itinerary
    itinerary = []
    landmark_list = list(descriptions.values())
    landmarks_per_day = max(1, len(landmark_list) // request.days_available)

    for day in range(1, request.days_available + 1):
        start_idx = (day - 1) * landmarks_per_day
        end_idx = start_idx + landmarks_per_day
        day_locations = landmark_list[start_idx:end_idx]

        if day_locations:
            day_itinerary = Itinerary(
                day=day,
                locations=day_locations,
                notes=f"Day {day}: Explore {', '.join(loc.landmark_name for loc in day_locations)}. "
                f"Budget 1-2 hours per location.",
            )
            itinerary.append(day_itinerary)

    # Calculate total distance (mock calculation)
    total_distance = len(landmark_list) * 50  # Assume 50km between landmarks on average

    travel_plan = TravelPlan(
        title=f"{request.days_available}-Day Scottish Landmarks Adventure",
        summary=f"An exciting {request.days_available}-day journey through Scotland's most iconic landmarks, "
        f"starting from {request.start_location}.",
        itinerary=itinerary,
        total_distance_km=float(total_distance),
        estimated_cost="£500-£2000 depending on accommodation and dining",
    )

    state["travel_plan"] = travel_plan
    state["current_step"] = "create_itinerary"

    return state


def create_travel_planner_graph():
    """
    Create and return the LangGraph state machine for travel planning.

    The graph orchestrates a 3-step workflow:
    1. Select Landmarks - Choose appropriate landmarks based on user interests
    2. Generate Descriptions - Use Gemini AI and tools to fetch photos/reviews
    3. Create Itinerary - Build day-by-day travel plan

    Returns:
        Compiled LangGraph graph
    """
    graph = StateGraph(PlannerState)

    # Add nodes
    graph.add_node("select_landmarks", select_landmarks_node)
    graph.add_node("generate_descriptions", generate_descriptions_node)
    graph.add_node("create_itinerary", create_itinerary_node)

    # Add edges
    graph.add_edge(START, "select_landmarks")
    graph.add_edge("select_landmarks", "generate_descriptions")
    graph.add_edge("generate_descriptions", "create_itinerary")
    graph.add_edge("create_itinerary", END)

    # Compile the graph
    compiled_graph = graph.compile()

    return compiled_graph
