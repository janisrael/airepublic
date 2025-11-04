# AWS EC2 Free Tier Compatibility Analysis

## Current Setup Resource Usage

### Memory (RAM) Requirements
- **Backend (Flask)**: ~1.4GB
- **Frontend (Vite)**: ~240MB  
- **PostgreSQL**: ~100-200MB (minimal)
- **Total Application RAM**: ~1.64GB

### Storage Requirements
- **Python venv**: 7.3GB
- **Node.js modules**: 221MB
- **PostgreSQL data**: 102MB (current)
- **Application code**: ~50MB
- **Logs/Cache**: Variable
- **Total Dependencies**: ~7.5GB+

### CPU Usage
- **Backend**: ~0.2-3% CPU (idle)
- **Frontend**: ~0.2% CPU (idle)
- **Normal operation**: Low CPU usage (external models)

---

## AWS EC2 Free Tier Specifications

### EC2 Instance Options

#### t2.micro (Free Tier Eligible)
- **vCPU**: 1 core
- **RAM**: 1 GiB (1024 MB)
- **Storage**: 30 GB EBS (General Purpose SSD)
- **Network**: Low to Moderate (Up to 5 Gbps)
- **CPU Credits**: Baseline 10% CPU, burst up to 100%
- **Free Tier**: 750 hours/month (for accounts created before July 15, 2025)

#### t3.micro (Free Tier Eligible) ⭐ **Recommended**
- **vCPU**: 1 core (better performance)
- **RAM**: 1 GiB (1024 MB)
- **Storage**: 30 GB EBS (General Purpose SSD)
- **Network**: Up to 5 Gbps (better than t2.micro)
- **CPU Credits**: Unlimited mode available, better baseline performance
- **Free Tier**: 750 hours/month (available for all accounts)
- **Performance**: ~20% faster CPU, better network performance

**Recommendation**: Use **t3.micro** - same free tier eligibility, better performance

### RDS PostgreSQL (Optional)
- **Instance**: db.t2.micro
- **RAM**: 1 GiB
- **Storage**: 20 GB (General Purpose SSD)
- **Free Tier**: 750 hours/month
- **Note**: Can run PostgreSQL on EC2 instead to save RDS allocation

---

## ⚠️ Compatibility Issues

### 1. **Memory Constraint (Critical)**
- **Problem**: Current setup uses ~1.64GB RAM, but Free Tier only provides 1GB
- **Impact**: Application will run out of memory, causing crashes/swap issues
- **Solution Required**: Optimize memory usage or use external RDS

### 2. **Storage Constraint**
- **Problem**: Python venv (7.3GB) + dependencies may exceed 30GB after OS (~8GB) and system files
- **Impact**: Limited space for application data and growth
- **Solution Required**: Optimize Python dependencies, use smaller venv, or clean unused packages

### 3. **Redis Dependency**
- **Current Status**: Optional (fails gracefully if Redis unavailable)
- **Code Location**: `backend/cache/redis_config.py`, `backend/services/optimized_api_service.py`
- **Impact**: Low - Redis is for caching/performance, not required for functionality

---

## ✅ What Works Well

### 1. **External Models**
- ✅ **Perfect for Free Tier**: Using external API models (NVIDIA, OpenAI, etc.) means:
  - No local model storage needed
  - No GPU requirements
  - Low compute requirements
  - API calls only consume bandwidth (unlimited on Free Tier)

### 2. **PostgreSQL**
- ✅ Can run on same EC2 instance (saves RDS allocation)
- ✅ Current database size (102MB) is very manageable
- ✅ Or use RDS Free Tier for better separation

### 3. **Low CPU Usage**
- ✅ Application is CPU-light (0.2-3% idle)
- ✅ Free Tier 1 vCPU is sufficient for moderate traffic

---

## 🎯 Recommended Optimizations for Free Tier

### Option 1: **Optimize Memory Usage** (Recommended)

#### Backend Memory Optimization
```bash
# 1. Use production mode (disable debug features)
DEBUG_MODE=false
FLASK_ENV=production

# 2. Disable auto-reload (saves memory)
AUTO_RELOAD=false

# 3. Use gunicorn with limited workers
# Instead of: python app_server_new.py
# Use: gunicorn -w 1 --threads 2 --bind 0.0.0.0:5001 app_server_new:app
```

#### Frontend Memory Optimization
```bash
# 1. Build for production (smaller footprint)
npm run build
# Serve static files with nginx instead of Vite dev server

# 2. Use production mode
NODE_ENV=production
```

#### PostgreSQL Optimization
```sql
-- Reduce PostgreSQL memory settings
shared_buffers = 128MB          # Down from default 256MB
effective_cache_size = 256MB    # Down from default 1GB
maintenance_work_mem = 64MB     # Down from default 128MB
work_mem = 4MB                  # Down from default 16MB
```

### Option 2: **Use RDS for PostgreSQL** (Better Separation)

**Benefits:**
- Frees up ~200MB RAM on EC2 instance
- Better for scaling later
- Automatic backups

**Setup:**
- Use RDS Free Tier (db.t2.micro, 20GB storage)
- Update `.env`: Point to RDS endpoint instead of localhost
- Saves EC2 memory for application

### Option 3: **Reduce Python Dependencies**

```bash
# Audit and remove unused packages
pip-autoremove <package-name>

# Use minimal Python installation
# Remove development dependencies
pip install --no-dev

# Consider using Alpine Linux base image (smaller)
```

### Option 4: **Make Redis Truly Optional**

Redis is already optional, but ensure graceful fallback:
- ✅ Already implemented in `redis_config.py` (catches exceptions)
- ✅ Cache misses are handled gracefully
- **Recommendation**: Skip Redis entirely on Free Tier (not critical)

---

## 📊 Recommended EC2 Free Tier Configuration

### Architecture Option A: All-in-One (Single EC2)
```
EC2 t3.micro (1GB RAM, 30GB storage) ⭐ Recommended
├── Backend (Flask) - optimized: ~500MB
├── Frontend (Nginx static) - ~50MB
├── PostgreSQL - optimized: ~150MB
└── System overhead - ~300MB
Total: ~1GB (tight but possible)
```

**Optimizations Needed:**
1. ✅ Use production builds (no dev servers)
2. ✅ Optimize PostgreSQL memory settings
3. ✅ Disable debug/auto-reload
4. ✅ Use Nginx for frontend (static files)
5. ✅ Skip Redis (optional anyway)

### Architecture Option B: EC2 + RDS (Recommended)
```
EC2 t3.micro (1GB RAM, 30GB storage) ⭐ Recommended
├── Backend (Flask) - optimized: ~500MB
├── Frontend (Nginx static) - ~50MB
└── System overhead - ~400MB

RDS db.t2.micro (1GB RAM, 20GB storage)
└── PostgreSQL database
```

**Benefits:**
- More breathing room on EC2 (200MB saved)
- Better separation of concerns
- Automatic backups
- Easier scaling later

---

## 🚀 Deployment Checklist for AWS EC2 Free Tier

### Pre-Deployment
- [ ] Optimize Python dependencies (remove unused packages)
- [ ] Build frontend for production (`npm run build`)
- [ ] Configure PostgreSQL for low memory
- [ ] Set `DEBUG_MODE=false` and `AUTO_RELOAD=false`
- [ ] Disable Redis (optional, not critical)
- [ ] Test with limited resources locally

### EC2 Instance Setup
- [ ] Choose **t3.micro** (recommended - better performance than t2.micro, same price/free tier)
- [ ] Use Ubuntu 22.04 LTS (small footprint)
- [ ] Configure security groups (ports 80, 443, 22, 5001)
- [ ] Set up swap space (2GB) as safety net
- [ ] Install dependencies (Python 3.10+, Node.js, PostgreSQL)

### Application Deployment
- [ ] Clone repository
- [ ] Create optimized `.env` file
- [ ] Install Python dependencies (production only)
- [ ] Build frontend (`npm run build`)
- [ ] Configure Nginx for frontend and reverse proxy
- [ ] Set up systemd services for backend
- [ ] Configure PostgreSQL with optimized settings
- [ ] Test all endpoints

### Monitoring
- [ ] Set up CloudWatch basic monitoring
- [ ] Monitor memory usage (`free -h`)
- [ ] Monitor disk usage (`df -h`)
- [ ] Set up alerts for high CPU/memory

---

## 💰 Cost Analysis (After Free Tier)

**After 12 months, if you exceed Free Tier:**

### EC2 t3.micro (On-Demand) ⭐ Recommended
- **Cost**: ~$7.50/month (730 hours) - slightly cheaper than t2.micro
- **Storage**: $0.10/GB/month (30GB = $3/month)
- **Total EC2**: ~$10.50/month
- **Better Performance**: ~20% faster CPU, better network

### EC2 t2.micro (On-Demand)
- **Cost**: ~$8.50/month (730 hours)
- **Storage**: $0.10/GB/month (30GB = $3/month)
- **Total EC2**: ~$11.50/month

### RDS db.t2.micro (Optional)
- **Cost**: ~$15/month (730 hours)
- **Storage**: $0.115/GB/month (20GB = $2.30/month)
- **Total RDS**: ~$17.30/month

### Total Estimated Cost
- **Option A (All-in-One)**: ~$11.50/month
- **Option B (EC2 + RDS)**: ~$28.80/month

**Recommendation**: Start with Option A, migrate to Option B if you need more resources.

---

## ⚡ Quick Optimization Script

Create `optimize_for_free_tier.sh`:

```bash
#!/bin/bash
# Optimize application for AWS EC2 Free Tier

# 1. Build frontend for production
cd frontend
npm run build
cd ..

# 2. Optimize Python dependencies
cd backend
pip install --upgrade pip
pip-autoremove -y $(pip list | grep -E "dev|test" | cut -d' ' -f1)

# 3. Configure PostgreSQL for low memory
sudo sed -i 's/shared_buffers = .*/shared_buffers = 128MB/' /etc/postgresql/*/main/postgresql.conf
sudo sed -i 's/effective_cache_size = .*/effective_cache_size = 256MB/' /etc/postgresql/*/main/postgresql.conf

# 4. Update .env for production
sed -i 's/DEBUG_MODE=true/DEBUG_MODE=false/' .env
sed -i 's/AUTO_RELOAD=true/AUTO_RELOAD=false/' .env

echo "✅ Optimized for Free Tier deployment"
```

---

## Summary

### ✅ **Can it run on Free Tier?**
**YES**, but with optimizations:
- Current memory usage (1.64GB) exceeds 1GB limit
- Storage (7.5GB+ deps) is manageable but tight
- **Solution**: Optimize memory usage, use production builds, consider RDS

### 🎯 **Recommendation**
1. **Short-term**: Optimize current setup (production mode, smaller footprint)
2. **Best approach**: Use RDS for PostgreSQL (saves 200MB RAM on EC2)
3. **Critical**: Build frontend for production (save 200MB+ RAM)
4. **Optional**: Skip Redis entirely (not critical for functionality)

### 📈 **Expected Performance**
- **Light traffic**: ✅ Excellent
- **Moderate traffic**: ✅ Good (with optimizations)
- **Heavy traffic**: ⚠️ May need upgrade (but Free Tier should handle 100-500 requests/day easily)

---

**Last Updated**: 2025-11-01  
**Author**: Agimat (Swordfish Project)

