# Scottish Landmarks Travel Planner - UI

A modern Svelte 5 web interface for the Scottish Landmarks travel planning application, with real-time WebSocket streaming for live AI-generated travel plan generation.

## What It Does

Interactive web app for creating personalized Scottish travel itineraries:
- Collects user preferences (days, interests, budget, starting location)
- Streams real-time travel plan generation with progress tracking
- Displays day-by-day itineraries with location details
- Shows embedded images and review links for each landmark
- Filters plans by landmark categories (castles, mountains, lochs, etc.)

## Setup

### Prerequisites
- Node.js 18+
- Backend service running on `http://localhost:8000`

### Installation

1. Navigate to the UI directory:
   ```bash
   cd 2025-11-01-scottish_landmarks/ui
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start development server:
   ```bash
   npm run dev
   ```

The app will be available at `http://localhost:5173`

### Production Build

```bash
npm run build
npm run preview
```

## Features

### Tech Stack
- **Svelte 5** - Modern reactive framework with runes
- **SvelteKit** - Full-stack framework with file-based routing
- **TypeScript** - Full type safety throughout
- **Bulma CSS** - Clean, modern responsive styling
- **Vite** - Fast build tool and dev server
- **WebSocket** - Real-time streaming communication

### Components

**TravelForm.svelte**
- User input form with validation
- Days available selector (1-14)
- Starting location input
- Budget level selection (Budget, Medium, Luxury)
- Interest categories checkboxes
- Real-time error feedback
- Loading state management

**TravelPlan.svelte**
- Trip summary statistics
- Day-by-day navigation tabs
- Location descriptions and details
- Embedded images with source attribution
- Review links with star ratings
- Hotspots (highlights within each location)

**API Service (lib/api.ts)**
- REST endpoint methods
- WebSocket streaming with progress tracking
- Automatic message parsing and error handling
- TypeScript interfaces matching backend schemas

### Styling
- Bulma CSS framework for base styling
- Component-scoped CSS in `routes/styles/`
- Responsive grid layouts
- Custom CSS variables for theming
- Mobile-first design

### API Integration
- RESTful endpoints for landmarks and workflow info
- WebSocket streaming for real-time plan generation
- Typed request/response models
- Progress tracking callbacks
- Error handling and recovery
