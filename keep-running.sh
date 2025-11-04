#!/bin/bash
# keep-running.sh
# Simple script to keep both servers running

echo "🚀 Starting AI Republic servers..."

# Kill any existing processes
pkill -f "python.*api_server" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start backend
echo "🔧 Starting backend..."
cd backend
python3 api_server.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Servers started!"
echo "📡 Backend: http://localhost:5000"
echo "🎨 Frontend: http://localhost:5173"
echo "📊 Dashboard: http://localhost:5173/dashboard"
echo ""
echo "🛑 To stop: pkill -f 'python.*api_server' && pkill -f 'vite'"
echo ""

# Keep script running
wait
