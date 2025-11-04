#!/bin/bash

# AI Republic Services Startup Script
# This script starts all required services for the AI Republic platform

echo "🚀 Starting AI Republic Services..."

# Function to check if a service is running
check_service() {
    if systemctl is-active --quiet $1; then
        echo "✅ $1 is already running"
        return 0
    else
        echo "❌ $1 is not running"
        return 1
    fi
}

# Function to start a service
start_service() {
    echo "🔄 Starting $1..."
    sudo systemctl start $1
    if systemctl is-active --quiet $1; then
        echo "✅ $1 started successfully"
    else
        echo "❌ Failed to start $1"
        return 1
    fi
}

# Start PostgreSQL
if ! check_service postgresql; then
    start_service postgresql
fi

# Start Redis/Valkey
if ! check_service valkey; then
    echo "🔄 Starting Valkey (Redis-compatible)..."
    sudo -u valkey /usr/bin/valkey-server --port 6379 --daemonize yes
    sleep 2
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Valkey started successfully"
    else
        echo "❌ Failed to start Valkey"
    fi
fi

# Check services status
echo ""
echo "📊 Service Status:"
echo "PostgreSQL: $(systemctl is-active postgresql)"
echo "Valkey (Redis): $(redis-cli ping 2>/dev/null || echo 'Not responding')"

# Test PostgreSQL connection
echo ""
echo "🔍 Testing PostgreSQL connection..."
cd backend
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from database.postgres_connection import test_connection
test_connection()
" 2>/dev/null

echo ""
echo "🎯 Services are ready!"
echo "📝 To start the backend server: cd backend && python3 app_server_new.py"
echo "📝 To start the frontend: cd frontend && npm run dev"