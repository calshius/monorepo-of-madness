# Scottish Landmarks Travel Planner - Backend

An agentic FastAPI backend that creates personalized travel plans through Scottish landmarks using LangGraph, LangChain tools, and Google Gemini AI.

## What It Does

Generates intelligent travel itineraries for Scotland by:
- Selecting landmarks based on user interests and available days
- Creating rich AI-generated descriptions for each location
- Fetching photos using Google Custom Search API
- Aggregating review links from multiple platforms
- Building day-by-day itineraries with recommended hotspots
- Streaming real-time plan generation via WebSocket

## Setup

### Prerequisites
- Python 3.12+
- Google Gemini API token
- Google Custom Search API key (optional, for real photo search)

### Installation

1. Navigate to the backend directory:
   ```bash
   cd 2025-11-01-scottish_landmarks/backend
   ```

2. Install dependencies with uv:
   ```bash
   uv sync
   ```

3. Create a `.env` file:
   ```bash
   GEMINI_TOKEN=your_gemini_token_here
   GOOGLE_SEARCH_API_KEY=your_google_search_key_here  # Optional
   ```

4. Run the application:
   ```bash
   python -m scottish_landmarks.main
   ```

The API will be available at `http://localhost:8000`

## Features

### Tech Stack
- **FastAPI** - Async web framework with automatic OpenAPI docs
- **LangGraph** - Multi-step agentic workflow orchestration
- **LangChain Tools** - `@tool` decorated functions for photo and review search
- **Google Gemini** - AI-powered location descriptions
- **Pydantic** - Data validation and serialization
- **WebSocket** - Real-time streaming communication

### LangGraph Workflow

Three-step agentic pipeline:

1. **Select Landmarks** - Matches user interests to available landmarks
2. **Generate Descriptions** - Uses Gemini AI + tools to fetch photos/reviews
3. **Create Itinerary** - Distributes landmarks across days with travel tips

### API Tools

**`search_landmark_photos`**
- Searches Google Custom Search API for landmark photos
- Returns URLs, sources, and titles
- Falls back gracefully if unavailable

**`search_landmark_reviews`**
- Aggregates review links from TripAdvisor, Google Maps, Booking.com
- Returns URLs, sources, and ratings

### Endpoints

**REST:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /api/travel/landmarks` - List Scottish landmarks
- `POST /api/travel/plan` - Generate travel plan

**WebSocket:**
- `WS /ws/travel-plan` - Stream plan generation with progress updates

### Available Landmarks

Edinburgh Castle, Loch Ness, Ben Nevis, Stirling Castle, Isle of Skye, Glencoe, Glasgow

### Landmark Categories

`castle`, `mountain`, `loch`, `historic_site`, `natural_wonder`, `city`, `island`
