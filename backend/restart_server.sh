#!/bin/bash

echo "🔄 Restarting AI Republic Backend Server..."

# Stop all existing processes
echo "🛑 Stopping existing server..."
pkill -9 -f app_server_new.py 2>/dev/null
sleep 3

echo "🚀 Starting fresh server..."
echo "📊 Server will run on port 5001"
echo "🔧 Using PostgreSQL + Redis"
echo ""

# Start the server with proper GPU memory management
CUDA_VISIBLE_DEVICES=0 PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512 python3 app_server_new.py
