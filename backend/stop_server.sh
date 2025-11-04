#!/bin/bash

echo "🛑 Stopping AI Republic Backend Server..."

# Kill all existing app_server_new.py processes
pkill -9 -f app_server_new.py 2>/dev/null

# Double-check and force kill any remaining processes
pkill -f "python3 app_server_new.py" 2>/dev/null

sleep 2

echo "✅ All server processes stopped"
echo "🔍 Checking for any remaining processes..."

# Check if any processes are still running
REMAINING=$(ps aux | grep app_server_new.py | grep -v grep | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo "✅ Confirmed: No server processes running"
else
    echo "⚠️  Warning: $REMAINING process(es) still running"
    ps aux | grep app_server_new.py | grep -v grep
fi
