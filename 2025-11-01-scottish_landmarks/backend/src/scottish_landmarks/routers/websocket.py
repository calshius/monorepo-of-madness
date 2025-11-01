"""WebSocket router for streaming travel plan generation."""
import asyncio
import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from scottish_landmarks.agent import create_travel_planner_graph
from scottish_landmarks.schemas import TravelPlanRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])

# Thread pool for running synchronous graph operations
_executor = None


def get_executor():
    """Get or create thread pool executor."""
    global _executor
    if _executor is None:
        _executor = __import__("concurrent.futures").futures.ThreadPoolExecutor(max_workers=2)
    return _executor


class ConnectionManager:
    """Manager for WebSocket connections."""

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and track a WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        self.active_connections.remove(websocket)


manager = ConnectionManager()


@router.websocket("/travel-plan")
async def websocket_travel_plan(websocket: WebSocket):
    """
    WebSocket endpoint for streaming travel plan generation.

    Expected message format:
    {
        "days_available": 5,
        "interests": ["castle", "mountain"],
        "start_location": "Edinburgh",
        "budget": "medium"
    }
    """
    await manager.connect(websocket)

    try:
        while True:
            # Receive request from client
            data = await websocket.receive_text()

            try:
                request_data = json.loads(data)
                request = TravelPlanRequest(**request_data)
            except (json.JSONDecodeError, ValidationError) as e:
                await websocket.send_json(
                    {"type": "error", "message": f"Invalid request format: {str(e)}"}
                )
                continue

            # Send start message
            await websocket.send_json({"type": "status", "message": "Starting travel plan generation..."})

            try:
                # Create and execute the graph
                graph = create_travel_planner_graph()

                initial_state = {
                    "request": request,
                    "selected_landmarks": [],
                    "landmark_descriptions": {},
                    "travel_plan": None,
                    "current_step": "start",
                }

                # Stream execution steps
                await websocket.send_json({"type": "step", "step": "selecting_landmarks", "progress": 0.25})
                await asyncio.sleep(0.1)
                
                await websocket.send_json({"type": "step", "step": "generating_descriptions", "progress": 0.6})
                await asyncio.sleep(0.1)

                # Execute the graph in a thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                executor = get_executor()
                result = await loop.run_in_executor(
                    executor,
                    graph.invoke,
                    initial_state
                )

                # Send final result
                if result.get("travel_plan"):
                    await websocket.send_json(
                        {
                            "type": "step",
                            "step": "creating_itinerary",
                            "progress": 1.0,
                        }
                    )
                    await websocket.send_json(
                        {
                            "type": "result",
                            "data": result["travel_plan"].model_dump(),
                        }
                    )
                else:
                    await websocket.send_json(
                        {"type": "error", "message": "Failed to generate travel plan"}
                    )

            except Exception as e:
                logger.error(f"Error generating travel plan: {e}")
                await websocket.send_json({"type": "error", "message": f"Generation failed: {str(e)}"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
