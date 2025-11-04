# AI Republic Setup Guide

This guide will help you set up the AI Republic platform with all required services.

## Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Redis/Valkey

## Quick Start

### 1. Start All Services
```bash
./start_services.sh
```

### 2. Start Backend Server
```bash
cd backend
python3 app_server_new.py
```

### 3. Start Frontend Server
```bash
cd frontend
npm run dev
```

## Manual Setup

### PostgreSQL Setup

1. **Install PostgreSQL:**
```bash
sudo dnf install postgresql postgresql-server postgresql-contrib
```

2. **Initialize and Start:**
```bash
sudo postgresql-setup --initdb
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

3. **Create Database and User:**
```bash
sudo -u postgres createuser --createdb --pwprompt ai_republic
# Enter password: admin123
sudo -u postgres createdb ai_republic_spirits
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ai_republic_spirits TO ai_republic;"
```

4. **Configure Authentication:**
```bash
sudo sed -i 's/ident/md5/g' /var/lib/pgsql/data/pg_hba.conf
sudo systemctl reload postgresql
```

### Redis/Valkey Setup

1. **Install Valkey (Redis-compatible):**
```bash
sudo dnf install valkey-compat-redis
```

2. **Start Valkey:**
```bash
sudo -u valkey /usr/bin/valkey-server --port 6379 --daemonize yes
```

3. **Test Connection:**
```bash
redis-cli ping
# Should return: PONG
```

### Environment Configuration

1. **Backend Environment:**
```bash
cd backend
cp .env.example .env
# Edit .env with your settings
```

2. **Frontend Environment:**
```bash
cd frontend
cp env.example .env
# Edit .env with your settings
```

## Environment Variables

### Backend (.env)
```bash
# PostgreSQL Database Configuration
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
BACKEND_HOST=localhost
DEBUG_MODE=true

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend (.env)
```bash
# Frontend API Configuration
VITE_V1_BASE_URL=http://localhost:5000/api
VITE_V2_BASE_URL=http://localhost:5000/api/v2
VITE_API_BASE_URL=http://localhost:5000/api/v2
VITE_AUTH_ENDPOINT=http://localhost:5000/api/auth
VITE_API_VERSION=v2
VITE_DEV_MODE=true
VITE_DEBUG_API_CALLS=false
```

## Service Management

### Start Services
```bash
# PostgreSQL
sudo systemctl start postgresql

# Redis/Valkey
sudo -u valkey /usr/bin/valkey-server --port 6379 --daemonize yes
```

### Stop Services
```bash
# PostgreSQL
sudo systemctl stop postgresql

# Redis/Valkey
sudo pkill -f valkey-server
```

### Check Service Status
```bash
# PostgreSQL
systemctl status postgresql

# Redis/Valkey
redis-cli ping
```

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Test connection
python3 -c "
from dotenv import load_dotenv
load_dotenv()
from database.postgres_connection import test_connection
test_connection()
"
```

### Redis Connection Issues
```bash
# Test connection
redis-cli ping

# Check if port is in use
sudo netstat -tlnp | grep 6379
```

### Backend Server Issues
```bash
# Check if server is running
ps aux | grep app_server_new.py

# Kill all backend processes
pkill -f app_server_new.py

# Restart server
cd backend && python3 app_server_new.py
```

## Development Workflow

1. **Start all services:** `./start_services.sh`
2. **Start backend:** `cd backend && python3 app_server_new.py`
3. **Start frontend:** `cd frontend && npm run dev`
4. **Access application:** http://localhost:5173

## Production Considerations

- Change default passwords
- Use strong SECRET_KEY
- Configure proper CORS origins
- Enable SSL/TLS
- Set up proper logging
- Configure firewall rules
- Set up monitoring and backups
