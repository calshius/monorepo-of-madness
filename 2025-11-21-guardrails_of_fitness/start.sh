#!/bin/bash

# Fitness Analysis Application - Startup Script

set -e

echo "Starting Fitness Analysis Application..."
echo ""

# Check if GEMINI_TOKEN is available (either as env var or in .env file)
if [ -z "$GEMINI_TOKEN" ]; then
    echo "GEMINI_TOKEN not found in environment, checking backend/.env..."
    if [ ! -f "backend/.env" ]; then
        echo "ERROR: GEMINI_TOKEN environment variable not set and backend/.env file not found!"
        echo "Either:"
        echo "  1. Export GEMINI_TOKEN as an environment variable, or"
        echo "  2. Copy backend/.env.example to backend/.env and configure your GEMINI_TOKEN"
        exit 1
    fi
    
    if ! grep -q "^GEMINI_TOKEN=..*" backend/.env; then
        echo "ERROR: GEMINI_TOKEN appears to be empty in backend/.env"
        echo "Please configure your Gemini API key"
        exit 1
    fi
    echo "Using GEMINI_TOKEN from backend/.env"
else
    echo "Using GEMINI_TOKEN from environment variable"
fi

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Start backend in background
echo "Starting backend server on http://localhost:8000..."
cd backend
python -m fitness_analysis.main > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
cd ..

# Wait for backend to start
echo "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "ERROR: Backend failed to start. Check backend.log for details."
    exit 1
fi

# Start frontend in background
echo "Starting frontend server on http://localhost:5173..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
cd ..

# Wait for frontend to start
echo "Waiting for frontend to initialize..."
sleep 3

# Check if frontend is running
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "ERROR: Frontend failed to start. Check frontend.log for details."
    echo "Cleaning up backend..."
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo ""
echo "Application started successfully!"
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Logs:"
echo "  Backend:  tail -f backend.log"
echo "  Frontend: tail -f frontend.log"
echo ""
echo "To stop the application, run: ./stop.sh"
