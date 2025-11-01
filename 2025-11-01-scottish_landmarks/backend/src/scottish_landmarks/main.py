"""Main FastAPI application for Scottish Landmarks Travel Planner."""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scottish_landmarks.config import settings
from scottish_landmarks.routers import travel, websocket

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="An agentic application for creating personalized travel plans through Scottish landmarks using LangGraph and Gemini",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(travel.router)
app.include_router(websocket.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "scottish-landmarks-travel-planner"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "endpoints": {
            "health": "/health",
            "landmarks": "/api/travel/landmarks",
            "workflow": "/api/travel/workflow",
            "plan": "/api/travel/plan",
            "websocket": "/ws/travel-plan",
        },
    }


def main():
    """Run the application."""
    import uvicorn

    uvicorn.run(
        "scottish_landmarks.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
