# Migration Plan: ai-refinement-dashboard to New Computer

## Analysis Summary

### Database System
- **PostgreSQL ONLY** - NO SQLite allowed (per codingrules.mdc)
- Database name: `ai_republic_spirits`
- User: `ai_republic`
- Password: `password` (code default) or `admin123` (SETUP.md)
- Host: `127.0.0.1` (IPv4)
- Port: `5432`

### Redis System
- Required for caching, sessions, rate limiting
- Host: `localhost`
- Port: `6379`
- Database: `0`
- Password: Optional (none by default)

### Key Findings from Documentation Review

1. **codingrules.mdc** - CRITICAL: PostgreSQL Only - NO SQLite
2. **SETUP.md** - Manual setup guide with PostgreSQL and Redis/Valkey
3. **DEPLOYMENT.md** - Production deployment guide
4. **RUN_EVERYTHING.md** - Shows backend .env structure
5. **CURRENT_ISSUES_SOLUTION.md** - Previously had SQLite fallback issues (now fixed)

### Current Configuration Issues Found

1. `env.example` file is incomplete - missing PostgreSQL/Redis variables
2. No `.env` file template with complete database/Redis config
3. Database name inconsistencies:
   - Code/SETUP.md: `ai_republic_spirits`
   - Docker: `ai_refinement_v2`
4. Password inconsistencies:
   - Code: `password`
   - SETUP.md: `admin123`
   - Docker: `airepublic123`

---

## Next Steps for Option A (Native Setup)

### Phase 1: Prerequisites Installation

#### 1.1 Install PostgreSQL 12+
```bash
# For Fedora/RHEL (your system)
sudo dnf install postgresql postgresql-server postgresql-contrib

# Initialize PostgreSQL
sudo postgresql-setup --initdb

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### 1.2 Install Redis 6+
```bash
# For Fedora/RHEL
sudo dnf install redis

# Or use Valkey (Redis-compatible)
sudo dnf install valkey-compat-redis

# Start and enable Redis/Valkey
sudo systemctl start redis  # or valkey
sudo systemctl enable redis  # or valkey
```

#### 1.3 Verify Python and Node.js
```bash
# Check Python 3.9+
python3 --version

# Check Node.js 16+
node --version
npm --version
```

---

### Phase 2: Database Setup

#### 2.1 Create PostgreSQL Database and User
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE ai_republic_spirits;

# Create user with password
CREATE USER ai_republic WITH PASSWORD 'password';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ai_republic_spirits TO ai_republic;

# Configure authentication (if needed)
# Edit /var/lib/pgsql/data/pg_hba.conf and change 'ident' to 'md5'
sudo sed -i 's/ident/md5/g' /var/lib/pgsql/data/pg_hba.conf
sudo systemctl reload postgresql

# Exit psql
\q
```

#### 2.2 Test PostgreSQL Connection
```bash
# Test connection
psql -h 127.0.0.1 -U ai_republic -d ai_republic_spirits

# Or test from Python
cd ai-refinement-dashboard/backend
python3 -c "
from database.postgres_connection import test_connection
test_connection()
"
```

---

### Phase 3: Redis Setup

#### 3.1 Verify Redis is Running
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# Check Redis status
sudo systemctl status redis
```

#### 3.2 Configure Redis (Optional)
```bash
# Edit Redis config (if needed)
sudo nano /etc/redis/redis.conf

# Key settings:
# - maxmemory 2gb
# - maxmemory-policy allkeys-lru
# - bind 127.0.0.1 (for security)

# Restart Redis after changes
sudo systemctl restart redis
```

---

### Phase 4: Application Configuration

#### 4.1 Create Complete .env File
**Location**: `/ai-refinement-dashboard/.env`

```bash
# PostgreSQL Database Configuration
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=ai_republic_spirits
POSTGRES_USER=ai_republic
POSTGRES_PASSWORD=password

# Redis/Valkey Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Server Configuration
BACKEND_PORT=5001
FRONTEND_PORT=5173
BACKEND_HOST=localhost
FRONTEND_HOST=localhost

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_TIMEOUT=60

# Training Configuration
DEFAULT_MAX_SAMPLES=1000
DEFAULT_TRAINING_EPOCHS=3
DEFAULT_LEARNING_RATE=0.0002
DEFAULT_BATCH_SIZE=4

# Evaluation Configuration
EVALUATION_TIMEOUT=60
EVALUATION_MAX_SAMPLES=3

# File Upload Configuration
MAX_UPLOAD_SIZE=52428800
AVATAR_MAX_SIZE=5242880
AVATAR_RESIZE_SIZE=128

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=backend/api_server.log

# Development Configuration
DEBUG_MODE=true
AUTO_RELOAD=true

# Security Configuration
SECRET_KEY=your-secret-key-here-change-in-production
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Frontend API Configuration
VITE_V1_BASE_URL=http://localhost:5001/api
VITE_V2_BASE_URL=http://localhost:5001/api/v2
VITE_API_BASE_URL=http://localhost:5001/api/v2
VITE_AUTH_ENDPOINT=http://localhost:5001/api/auth
VITE_API_VERSION=v2
VITE_DEV_MODE=true
VITE_DEBUG_API_CALLS=false
```

---

### Phase 5: Database Initialization

#### 5.1 Initialize PostgreSQL Database
```bash
cd ai-refinement-dashboard/backend

# Run initialization script
python3 scripts/init_postgres_spirits.py

# This will:
# - Test PostgreSQL connection
# - Create database if missing
# - Create all 12 tables
```

#### 5.2 Run Database Setup
```bash
# Run complete setup (includes seeding)
python3 scripts/setup_postgres_spirits.py

# Or use Makefile command
cd ..
make db-create
```

#### 5.3 Verify Tables Created
```bash
# Connect to database
psql -h 127.0.0.1 -U ai_republic -d ai_republic_spirits

# List tables
\dt

# Should see:
# - spirits_registry
# - minion_spirits
# - spirit_mastery
# - spirit_bundles
# - subscription_plans
# - user_spirit_purchases
# - user_subscriptions
# - user_points
# - points_transactions
# - user_spirit_access
# - tools_registry
# - minions

\q
```

---

### Phase 6: Application Setup

#### 6.1 Python Environment Setup
```bash
cd ai-refinement-dashboard

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### 6.2 Frontend Setup
```bash
cd frontend

# Install Node.js dependencies
npm install

# Verify installation
npm list --depth=0
```

#### 6.3 Test Connections
```bash
cd ../backend

# Test PostgreSQL connection
python3 -c "
from database.postgres_connection import test_connection
test_connection()
"

# Test Redis connection
python3 -c "
from cache.redis_config import redis_manager
redis_manager.redis_client.ping()
print('✅ Redis connection successful')
"
```

---

### Phase 7: Start Services

#### 7.1 Start Database Services
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Start Redis
sudo systemctl start redis

# Verify services are running
sudo systemctl status postgresql
sudo systemctl status redis
```

#### 7.2 Start Application
```bash
cd ai-refinement-dashboard

# Option 1: Use start_services.sh
./start_services.sh

# Then start backend
cd backend
python3 app_server_new.py

# Option 2: Use Makefile
make dev

# Option 3: Manual start
# Terminal 1: Backend
cd backend
python3 app_server_new.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

### Phase 8: Verification & Testing

#### 8.1 Check Service Status
```bash
# Use Makefile status command
make status

# Should show:
# - Backend V2: ✅ Running
# - Frontend: ✅ Running
# - Redis: ✅ Running
# - PostgreSQL: ✅ Running
```

#### 8.2 Test API Endpoints
```bash
# Health check
curl http://localhost:5001/api/status

# Test PostgreSQL connection endpoint
curl http://localhost:5001/api/health

# Test Redis connection
redis-cli ping
```

#### 8.3 Access Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5001
- **API Documentation**: http://localhost:5001/docs

---

## Checklist Summary

### Prerequisites
- [ ] PostgreSQL 12+ installed
- [ ] Redis 6+ installed
- [ ] Python 3.9+ installed
- [ ] Node.js 16+ installed

### Database Setup
- [ ] PostgreSQL service started and enabled
- [ ] Database `ai_republic_spirits` created
- [ ] User `ai_republic` created with password
- [ ] Permissions granted
- [ ] PostgreSQL authentication configured
- [ ] Connection tested

### Redis Setup
- [ ] Redis service started and enabled
- [ ] Redis connection tested (redis-cli ping)
- [ ] Redis configuration optimized (optional)

### Application Configuration
- [ ] `.env` file created with all variables
- [ ] PostgreSQL credentials configured
- [ ] Redis credentials configured
- [ ] Frontend API URLs configured

### Database Initialization
- [ ] Database initialization script run
- [ ] All 12 tables created
- [ ] Tables verified in database
- [ ] Seed data loaded (if needed)

### Application Setup
- [ ] Python virtual environment created
- [ ] Python dependencies installed
- [ ] Node.js dependencies installed
- [ ] Backend connection to PostgreSQL tested
- [ ] Backend connection to Redis tested

### Service Startup
- [ ] PostgreSQL service running
- [ ] Redis service running
- [ ] Backend server started
- [ ] Frontend server started

### Verification
- [ ] All services status checked
- [ ] API endpoints tested
- [ ] Frontend accessible
- [ ] Backend API accessible

---

## Important Notes

1. **NO SQLite**: The system uses PostgreSQL only. Remove any SQLite references.

2. **Password Standardization**: Choose one password standard:
   - Recommended: `password` (matches code defaults)

3. **Database Name**: Use `ai_republic_spirits` (matches code/SETUP.md)

4. **Network Configuration**: 
   - PostgreSQL uses `127.0.0.1` (IPv4)
   - Redis uses `localhost`

5. **Port Conflicts**: 
   - Backend: 5001 (V2 server)
   - Frontend: 5173
   - PostgreSQL: 5432
   - Redis: 6379

6. **Environment Variables**: All configuration should be in `.env` file in root directory.

---

## Troubleshooting

### PostgreSQL Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check if database exists
sudo -u postgres psql -l | grep ai_republic_spirits

# Test connection manually
psql -h 127.0.0.1 -U ai_republic -d ai_republic_spirits
```

### Redis Connection Issues
```bash
# Check Redis status
sudo systemctl status redis

# Test connection
redis-cli ping

# Check if port is in use
sudo netstat -tlnp | grep 6379
```

### Backend Connection Issues
```bash
# Test from Python
cd backend
python3 -c "
from database.postgres_connection import test_connection
test_connection()
"

# Test Redis
python3 -c "
from cache.redis_config import redis_manager
print(redis_manager.redis_client.ping())
"
```

---

**Ready to proceed with Phase 1: Prerequisites Installation**





