#!/bin/bash

# Quick Start Script for AI Republic Training Center
# Simple script to start both servers quickly

echo "🚀 Quick Start - AI Republic Training Center"

# Kill existing processes
pkill -f "python.*api_server" 2>/dev/null
pkill -f "vite" 2>/dev/null
sleep 2

# Start backend
echo "🔧 Starting backend..."
cd backend
python3 api_server.py &
BACKEND_PID=$!
cd ..

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for servers to start
sleep 5

echo ""
echo "✅ Servers started!"
echo "📡 Backend: http://localhost:5000"
echo "🎨 Frontend: http://localhost:5173"
echo ""
echo "🛑 To stop: pkill -f 'python.*api_server' && pkill -f 'vite'"
echo ""

# Keep script running
wait
