#!/bin/bash

# Kill any existing processes on ports 8000 and 5173
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

echo "🚀 Starting EMS V2.0..."

# Start Backend
echo "🔹 Starting Backend (FastAPI)..."
# Run from root so 'backend' is treated as a package
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start Frontend
echo "🔹 Starting Frontend (React)..."
cd frontend
npm run dev -- --port 5173 &
FRONTEND_PID=$!
cd ..

echo "✅ System Online!"
echo "   - Frontend: http://localhost:5173"
echo "   - Backend:  http://localhost:8000"
echo "Press CTRL+C to stop."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
