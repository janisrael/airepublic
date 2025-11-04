#!/bin/bash

echo "🛑 Stopping all existing server processes..."
# Kill all existing app_server_new.py processes
pkill -9 -f app_server_new.py 2>/dev/null
sleep 3

echo "🧹 Cleaning up any remaining processes..."
# Double-check and force kill any remaining processes
pkill -f "python3 app_server_new.py" 2>/dev/null
sleep 2

echo "✅ All processes stopped"

echo "🚀 Starting AI Republic Backend Server..."
echo "📊 Server will run on port 5001"
echo "🔧 Using PostgreSQL + Redis"
echo ""

# Start the server with proper GPU memory management
CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 python3 app_server_new.py

echo ""
echo "🛑 Server stopped"
