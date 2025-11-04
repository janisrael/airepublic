
🚀 How to Run Everything:

Option 1: Quick Start

./start_services.sh
cd backend && python3 app_server_new.py
cd frontend && npm run dev

Option 2: Manual Start

# Start services
sudo systemctl start postgresql
sudo -u valkey /usr/bin/valkey-server --port 6379 --daemonize yes

# Start backend
cd backend && python3 app_server_new.py

# Start frontend  
cd frontend && npm run dev

ackend .env includes:
# PostgreSQL Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_republic_spirits
POSTGRES_USER=ai_republic
POSTGRES_PASSWORD=admin123

# Redis/Valkey Configuration  
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Server Configuration
BACKEND_PORT=5000
DEBUG_MODE=true