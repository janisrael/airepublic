#!/bin/bash

# AI Republic Training Center - Development Startup Script
# This script starts both backend and frontend servers

echo "🚀 Starting AI Republic Training Center..."
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

# Function to kill existing processes
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    pkill -f "python.*api_server" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo -e "${RED}❌ Error: Please run this script from the ai-refinement-dashboard root directory${NC}"
    exit 1
fi

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Error: Python3 is not installed${NC}"
    exit 1
fi

# Check Node.js installation
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Error: Node.js is not installed${NC}"
    exit 1
fi

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
    cd frontend
    npm install
    cd ..
fi

# Check ports
echo -e "${BLUE}🔍 Checking ports...${NC}"
if ! check_port 5000; then
    echo -e "${YELLOW}⚠️  Backend port 5000 is in use. Attempting to free it...${NC}"
    pkill -f "python.*api_server" 2>/dev/null
    sleep 2
fi

if ! check_port 5173; then
    echo -e "${YELLOW}⚠️  Frontend port 5173 is in use. Attempting to free it...${NC}"
    pkill -f "vite" 2>/dev/null
    sleep 2
fi

# Start backend server
echo -e "${BLUE}🔧 Starting backend server (Flask API)...${NC}"
cd backend
python3 api_server.py > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start. Check backend.log for details${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Backend server started (PID: $BACKEND_PID)${NC}"

# Start frontend server
echo -e "${BLUE}🎨 Starting frontend server (Vite)...${NC}"
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait a moment for frontend to start
sleep 3

# Check if frontend started successfully
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Frontend failed to start. Check frontend.log for details${NC}"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"

# Display status
echo ""
echo -e "${GREEN}🎉 AI Republic Training Center is running!${NC}"
echo "=========================================="
echo -e "${BLUE}📡 Backend API:${NC}  http://localhost:5000"
echo -e "${BLUE}🎨 Frontend UI:${NC}  http://localhost:5173"
echo -e "${BLUE}📊 API Docs:${NC}     http://localhost:5000/api/docs"
echo ""
echo -e "${YELLOW}📝 Logs:${NC}"
echo -e "   Backend:  tail -f backend.log"
echo -e "   Frontend: tail -f frontend.log"
echo ""
echo -e "${YELLOW}🛑 To stop:${NC} Press Ctrl+C or run: pkill -f 'python.*api_server' && pkill -f 'vite'"
echo ""

# Keep script running and show logs
echo -e "${BLUE}📋 Live logs (Ctrl+C to stop):${NC}"
echo "=========================================="

# Function to show logs
show_logs() {
    while true; do
        if [ -f "backend.log" ] && [ -f "frontend.log" ]; then
            echo -e "\n${GREEN}🔄 Refreshing logs...${NC}"
            echo -e "${BLUE}--- Backend Logs (last 5 lines) ---${NC}"
            tail -n 5 backend.log 2>/dev/null || echo "No backend logs yet"
            echo -e "${BLUE}--- Frontend Logs (last 5 lines) ---${NC}"
            tail -n 5 frontend.log 2>/dev/null || echo "No frontend logs yet"
        fi
        sleep 10
    done
}

# Show logs in background
show_logs &
LOGS_PID=$!

# Wait for user interrupt
wait

# Cleanup on exit
cleanup
