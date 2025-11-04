#!/bin/bash
# start.sh
# Description: Safely start the AI-Refinement-Dashboard project.
# It detects zombies, frees ports, checks GPU health, and runs backend/frontend from the correct base directory.

# -------------------------------
# Configuration
# -------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASE_DIR="$SCRIPT_DIR"  # Use script's directory as base
V2_BACKEND_PORT=5001  # V2 server (PostgreSQL + SQLAlchemy)
FRONTEND_PORT=5173
LOG_FILE="$BASE_DIR/start.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# -------------------------------
# Functions
# -------------------------------
log() {
    echo -e "[`date +"%Y-%m-%d %H:%M:%S"`] $1" | tee -a "$LOG_FILE"
}

kill_port() {
    PORT=$1
    PID=$(lsof -t -i:$PORT 2>/dev/null)
    if [ -n "$PID" ]; then
        log "${YELLOW}Port $PORT is in use by PID $PID. Killing process...${NC}"
        kill -9 $PID 2>/dev/null
        sleep 1
    else
        log "${GREEN}Port $PORT is free.${NC}"
    fi
}

kill_zombie_python() {
    ZOMBIES=$(ps aux | awk '{ if ($8 == "Z" && $11 ~ /python/) print $2 }' 2>/dev/null)
    if [ -n "$ZOMBIES" ]; then
        log "${YELLOW}Found zombie Python processes: $ZOMBIES. Killing them...${NC}"
        kill -9 $ZOMBIES 2>/dev/null
        sleep 1
    else
        log "${GREEN}No zombie Python processes found.${NC}"
    fi
}

kill_stuck_processes() {
    # Kill existing backend/frontend processes more specifically
    pkill -f "python.*api_server" 2>/dev/null
    pkill -f "python.*app_server" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    pkill -f "npm.*dev" 2>/dev/null
    log "${GREEN}Cleaned up existing backend/frontend processes.${NC}"
}

check_gpu() {
    if command -v nvidia-smi &> /dev/null; then
        log "${BLUE}Checking GPU status...${NC}"
        nvidia-smi --query-gpu=name,memory.total,memory.used,utilization.gpu --format=csv,noheader,nounits | tee -a "$LOG_FILE"
    else
        log "${YELLOW}nvidia-smi not found. Skipping GPU check.${NC}"
    fi
}

start_postgresql() {
    log "${BLUE}🐘 Checking PostgreSQL status...${NC}"
    
    # Check if PostgreSQL is running
    if pg_isready -q; then
        log "${GREEN}✅ PostgreSQL is already running${NC}"
        return 0
    fi
    
    log "${YELLOW}⚠️  PostgreSQL is not running. Attempting to start...${NC}"
    
    # Try to start PostgreSQL (this might require sudo)
    if command -v systemctl &> /dev/null; then
        log "${BLUE}Starting PostgreSQL via systemctl...${NC}"
        sudo systemctl start postgresql 2>/dev/null || {
            log "${YELLOW}⚠️  Could not start PostgreSQL via systemctl. Please start it manually.${NC}"
            log "${YELLOW}   Run: sudo systemctl start postgresql${NC}"
            return 1
        }
    elif command -v pg_ctl &> /dev/null; then
        log "${BLUE}Starting PostgreSQL via pg_ctl...${NC}"
        pg_ctl start -D /var/lib/pgsql/data 2>/dev/null || {
            log "${YELLOW}⚠️  Could not start PostgreSQL via pg_ctl. Please start it manually.${NC}"
            return 1
        }
    else
        log "${RED}❌ PostgreSQL tools not found. Please install PostgreSQL and start it manually.${NC}"
        return 1
    fi
    
    # Wait for PostgreSQL to be ready
    log "${BLUE}Waiting for PostgreSQL to be ready...${NC}"
    for i in {1..30}; do
        if pg_isready -q; then
            log "${GREEN}✅ PostgreSQL is now running${NC}"
            return 0
        fi
        sleep 1
    done
    
    log "${RED}❌ PostgreSQL failed to start within 30 seconds${NC}"
    return 1
}

check_dependencies() {
    log "${BLUE}Checking dependencies...${NC}"
    
    # Ensure we're in the correct directory
    log "${BLUE}📍 Current directory: $(pwd)${NC}"
    log "${BLUE}📍 Script directory: $BASE_DIR${NC}"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log "${RED}❌ Error: Python3 is not installed${NC}"
        exit 1
    fi
    log "${GREEN}✅ Python3 found${NC}"
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log "${RED}❌ Error: Node.js is not installed${NC}"
        exit 1
    fi
    log "${GREEN}✅ Node.js found${NC}"
    
    # Check if we're in the right directory
    if [ ! -d "$BASE_DIR/backend" ] || [ ! -d "$BASE_DIR/frontend" ]; then
        log "${RED}❌ Error: Backend or frontend directory not found in $BASE_DIR${NC}"
        log "${RED}❌ Please run this script from the ai-refinement-dashboard root directory${NC}"
        exit 1
    fi
    log "${GREEN}✅ Project structure verified${NC}"
}

install_frontend_deps() {
    if [ ! -d "$BASE_DIR/frontend/node_modules" ]; then
        log "${YELLOW}📦 Installing frontend dependencies...${NC}"
        cd "$BASE_DIR/frontend"
        npm install
        cd "$BASE_DIR"
        log "${GREEN}✅ Frontend dependencies installed${NC}"
    else
        log "${GREEN}✅ Frontend dependencies already installed${NC}"
    fi
}

run_backend() {
    log "${BLUE}🚀 Starting V2 backend server (PostgreSQL + SQLAlchemy)...${NC}"
    cd "$BASE_DIR/backend"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        log "${YELLOW}📦 Creating virtual environment...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment and install dependencies
    source venv/bin/activate
    pip install -r requirements.txt > /dev/null 2>&1
    
    # Start the V2 backend
    nohup python app_server_new.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    cd "$BASE_DIR"
    
    # Wait a moment for backend to start
    sleep 3
    
    # Check if backend started successfully
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        log "${RED}❌ Backend failed to start. Check backend.log for details${NC}"
        exit 1
    fi
    
    log "${GREEN}✅ V2 backend server started (PID: $BACKEND_PID) on port 5001${NC}"
    echo $BACKEND_PID > backend.pid
}

run_frontend() {
    log "${BLUE}🎨 Starting frontend server (Vite)...${NC}"
    cd "$BASE_DIR/frontend"
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd "$BASE_DIR"
    
    # Wait a moment for frontend to start
    sleep 5
    
    # Check if frontend started successfully
    if ! kill -0 $FRONTEND_PID 2>/dev/null; then
        log "${RED}❌ Frontend failed to start. Check frontend.log for details${NC}"
        exit 1
    fi
    
    log "${GREEN}✅ Frontend server started (PID: $FRONTEND_PID)${NC}"
    echo $FRONTEND_PID > frontend.pid
}

verify_servers() {
    log "${BLUE}🔍 Verifying servers are accessible...${NC}"
    
    # Check backend
    if curl -s -f http://localhost:$V2_BACKEND_PORT/health > /dev/null 2>&1; then
        log "${GREEN}✅ Backend server is accessible${NC}"
    else
        log "${YELLOW}⚠️  Backend server may not be fully ready yet${NC}"
    fi
    
    # Check frontend
    if curl -s -f http://localhost:$FRONTEND_PORT > /dev/null 2>&1; then
        log "${GREEN}✅ Frontend server is accessible${NC}"
    else
        log "${YELLOW}⚠️  Frontend server may not be fully ready yet${NC}"
    fi
}

show_status() {
    echo ""
    log "${GREEN}🎉 AI Republic is running!${NC}"
    echo "=========================================="
    echo -e "${BLUE}🚀 Backend API:${NC}  http://localhost:$V2_BACKEND_PORT"
    echo -e "${BLUE}🎨 Frontend UI:${NC}  http://localhost:$FRONTEND_PORT"
    echo -e "${BLUE}📊 Dashboard:${NC}    http://localhost:$FRONTEND_PORT/dashboard"
    echo -e "${BLUE}🔧 Minion Builder:${NC} http://localhost:$FRONTEND_PORT/minion-builder"
    echo ""
    echo -e "${YELLOW}📝 Logs:${NC}"
    echo -e "   Backend:  tail -f $BASE_DIR/backend.log"
    echo -e "   Frontend: tail -f $BASE_DIR/frontend.log"
    echo ""
    echo -e "${YELLOW}🛑 To stop:${NC} Press Ctrl+C or run: pkill -f 'python.*app_server' && pkill -f 'vite'"
    echo ""
}

cleanup() {
    log "${YELLOW}🛑 Shutting down servers...${NC}"
    
    # Shutdown backend
    if [ -f "$BASE_DIR/backend.pid" ]; then
        BACKEND_PID=$(cat "$BASE_DIR/backend.pid")
        kill $BACKEND_PID 2>/dev/null
        rm -f "$BASE_DIR/backend.pid"
    fi
    pkill -f "python.*app_server" 2>/dev/null
    
    # Shutdown frontend
    if [ -f "$BASE_DIR/frontend.pid" ]; then
        FRONTEND_PID=$(cat "$BASE_DIR/frontend.pid")
        kill $FRONTEND_PID 2>/dev/null
        rm -f "$BASE_DIR/frontend.pid"
    fi
    pkill -f "vite" 2>/dev/null
    
    log "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# -------------------------------
# Execution
# -------------------------------
log "${BLUE}=================== Starting AI-Refinement-Dashboard ===================${NC}"

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Step 1: Check dependencies
check_dependencies

# Step 2: Kill processes using ports
log "${BLUE}🔍 Checking and freeing ports...${NC}"
kill_port $V2_BACKEND_PORT
kill_port $FRONTEND_PORT

# Step 3: Kill zombie Python processes
log "${BLUE}🧟 Checking for zombie processes...${NC}"
kill_zombie_python

# Step 4: Kill stuck frontend processes
log "${BLUE}🧹 Cleaning up existing processes...${NC}"
kill_stuck_processes

# Step 5: Check GPU health
log "${BLUE}🎮 Checking GPU health...${NC}"
check_gpu

# Step 6: Install frontend dependencies
install_frontend_deps

# Step 7: Navigate to base directory
cd "$BASE_DIR" || { log "${RED}Failed to change directory to $BASE_DIR. Exiting.${NC}"; exit 1; }

# Step 8: Run backend and frontend
run_backend
run_frontend

# Step 9: Verify both servers are accessible
verify_servers

# Step 10: Show status
show_status

# Step 11: Keep script running and show logs
log "${BLUE}📋 Live logs (Ctrl+C to stop):${NC}"
echo "=========================================="

# Function to show logs
show_logs() {
    while true; do
        if [ -f "$BASE_DIR/frontend.log" ]; then
            echo -e "\n${GREEN}🔄 Refreshing logs...${NC}"
            echo -e "${BLUE}--- Frontend Logs (last 3 lines) ---${NC}"
            tail -n 3 "$BASE_DIR/frontend.log" 2>/dev/null || echo "No frontend logs yet"
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
