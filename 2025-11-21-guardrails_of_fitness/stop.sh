#!/bin/bash

# Fitness Analysis Application - Stop Script

echo "Stopping Fitness Analysis Application..."

# Stop backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        rm backend.pid
    else
        echo "Backend process not running"
        rm backend.pid
    fi
else
    echo "No backend.pid file found"
fi

# Stop frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        rm frontend.pid
    else
        echo "Frontend process not running"
        rm frontend.pid
    fi
else
    echo "No frontend.pid file found"
fi

# Also kill any remaining node/vite processes
pkill -f "vite dev" 2>/dev/null || true

# Kill any remaining python fitness_analysis processes
pkill -f "fitness_analysis.main" 2>/dev/null || true

echo "Application stopped"
