#!/bin/bash

# GitHub Agentic Workflows Demo - Dev Script
# Usage: ./startup.sh        (start backend + frontend)
#        ./startup.sh stop   (tear down both)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

stop_services() {
    echo "Stopping services..."

    if [ -f "backend.pid" ]; then
        PID=$(cat backend.pid)
        if kill -0 "$PID" 2>/dev/null; then
            echo "  Stopping backend (PID: $PID)"
            kill "$PID"
        fi
        rm -f backend.pid
    fi

    if [ -f "frontend.pid" ]; then
        PID=$(cat frontend.pid)
        if kill -0 "$PID" 2>/dev/null; then
            echo "  Stopping frontend (PID: $PID)"
            kill "$PID"
        fi
        rm -f frontend.pid
    fi

    pkill -f "uvicorn src.main:app" 2>/dev/null || true
    pkill -f "vite dev" 2>/dev/null || true

    echo "Done."
}

start_services() {
    # Clean up any leftover processes
    stop_services 2>/dev/null

    echo ""
    echo "Starting services..."

    # Backend
    echo "  Backend → http://localhost:8000"
    cd backend
    uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
    echo $! > ../backend.pid
    cd ..

    sleep 2
    if ! kill -0 "$(cat backend.pid)" 2>/dev/null; then
        echo "  ERROR: Backend failed to start. Check backend.log"
        exit 1
    fi

    # Frontend
    echo "  Frontend → http://localhost:5173"
    cd frontend
    npm run dev > ../frontend.log 2>&1 &
    echo $! > ../frontend.pid
    cd ..

    sleep 2
    if ! kill -0 "$(cat frontend.pid)" 2>/dev/null; then
        echo "  ERROR: Frontend failed to start. Check frontend.log"
        stop_services
        exit 1
    fi

    echo ""
    echo "Running! Logs:"
    echo "  tail -f backend.log"
    echo "  tail -f frontend.log"
    echo ""
    echo "Stop with: ./startup.sh stop"
}

case "${1:-start}" in
    stop)  stop_services ;;
    start) start_services ;;
    *)     echo "Usage: ./startup.sh [start|stop]"; exit 1 ;;
esac
