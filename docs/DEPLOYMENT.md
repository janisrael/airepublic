# AI Republic Dashboard - Professional Deployment Guide

## 🚀 Production Deployment

This guide covers deploying the AI Republic Dashboard in a production environment with enterprise-grade features.

## 📋 Prerequisites

### System Requirements
- **OS**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **CPU**: 4+ cores recommended
- **RAM**: 8GB+ recommended
- **Storage**: 100GB+ SSD recommended
- **Network**: Stable internet connection

### Software Requirements
- Docker & Docker Compose
- PostgreSQL 13+
- Redis 6+
- Nginx (for reverse proxy)
- SSL certificates

## 🐳 Docker Deployment (Recommended)

### 1. Production Environment Setup

```bash
# Clone repository
git clone https://github.com/airepublic/dashboard.git
cd dashboard

# Copy production environment
cp .env.production .env

# Edit configuration
nano .env
```

### 2. Configure Production Environment

```bash
# .env production configuration
FLASK_ENV=production
DEBUG_MODE=false
DATABASE_URL=postgresql://user:pass@postgres:5432/ai_refinement_v2
REDIS_URL=redis://redis:6379/0
JWT_SECRET_KEY=your-super-secure-secret-key-here
CORS_ORIGINS=https://yourdomain.com
```

### 3. Deploy with Docker Compose

```bash
# Build and start services
make docker-build
make docker-up

# Or manually
docker-compose -f docker-compose.prod.yml up -d
```

### 4. Initialize Database

```bash
# Create database tables
docker-compose exec backend-v2 python create_v2_tables.py

# Create admin user
docker-compose exec backend-v2 python create_admin_user.py
```

## 🔧 Manual Deployment

### 1. System Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3.11 python3.11-venv nodejs npm postgresql redis-server nginx
```

### 2. Database Setup

```bash
# Create PostgreSQL database
sudo -u postgres psql
CREATE DATABASE ai_refinement_v2;
CREATE USER airepublic WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE ai_refinement_v2 TO airepublic;
\q
```

### 3. Application Deployment

```bash
# Setup Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup frontend
cd frontend
npm ci --production
npm run build
cd ..

# Start services
make dev
```

### 4. Nginx Configuration

```nginx
# /etc/nginx/sites-available/ai-republic
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Frontend
    location / {
        proxy_pass http://localhost:5173;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 🔐 Security Configuration

### 1. Firewall Setup

```bash
# Configure UFW
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. SSL/TLS Configuration

```bash
# Let's Encrypt SSL
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. Security Headers

```nginx
# Add to Nginx configuration
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 📊 Monitoring & Logging

### 1. Prometheus Setup

```bash
# Start monitoring stack
make monitor

# Access monitoring
# Prometheus: http://yourdomain.com:9090
# Grafana: http://yourdomain.com:3000
```

### 2. Log Management

```bash
# Configure log rotation
sudo nano /etc/logrotate.d/ai-republic

# Log rotation configuration
/var/log/ai-republic/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
}
```

### 3. Health Checks

```bash
# Create health check script
cat > /usr/local/bin/ai-republic-health.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:5001/api/status || exit 1
curl -f http://localhost:5173 || exit 1
redis-cli ping || exit 1
EOF

chmod +x /usr/local/bin/ai-republic-health.sh

# Add to crontab
echo "*/5 * * * * /usr/local/bin/ai-republic-health.sh" | crontab -
```

## 🔄 Backup & Recovery

### 1. Database Backup

```bash
# Create backup script
cat > /usr/local/bin/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/ai-republic"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
pg_dump ai_refinement_v2 > $BACKUP_DIR/db_backup_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/db_backup_$DATE.sql

# Keep only last 30 days
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup-db.sh

# Schedule backup
echo "0 2 * * * /usr/local/bin/backup-db.sh" | crontab -
```

### 2. Application Backup

```bash
# Full application backup
tar -czf ai-republic-backup-$(date +%Y%m%d).tar.gz \
    --exclude=node_modules \
    --exclude=venv \
    --exclude=.git \
    --exclude=logs \
    .
```

## 🚀 Performance Optimization

### 1. Redis Optimization

```bash
# Redis configuration optimization
echo "maxmemory 2gb" >> /etc/redis/redis.conf
echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
systemctl restart redis
```

### 2. PostgreSQL Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

### 3. Application Optimization

```bash
# Enable Gunicorn for production
pip install gunicorn

# Start with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 backend.app_server_new:app
```

## 🔍 Troubleshooting

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check PostgreSQL status
   sudo systemctl status postgresql
   
   # Check connection
   psql -h localhost -U airepublic -d ai_refinement_v2
   ```

2. **Redis Connection Errors**
   ```bash
   # Check Redis status
   sudo systemctl status redis
   
   # Test connection
   redis-cli ping
   ```

3. **Port Conflicts**
   ```bash
   # Check port usage
   sudo netstat -tlnp | grep :5001
   
   # Kill conflicting processes
   sudo kill -9 $(lsof -ti:5001)
   ```

### Log Analysis

```bash
# View application logs
tail -f backend/api_server_v2.log
tail -f frontend/frontend.log

# View system logs
sudo journalctl -u ai-republic -f
```

## 📈 Scaling

### Horizontal Scaling

1. **Load Balancer Configuration**
   ```nginx
   upstream backend {
       server 127.0.0.1:5001;
       server 127.0.0.1:5002;
       server 127.0.0.1:5003;
   }
   ```

2. **Database Scaling**
   - Read replicas for read-heavy workloads
   - Connection pooling with PgBouncer
   - Database sharding for very large datasets

3. **Cache Scaling**
   - Redis Cluster for high availability
   - CDN for static assets
   - Application-level caching

## 🎯 Maintenance

### Regular Maintenance Tasks

1. **Weekly**
   - Check disk space
   - Review logs for errors
   - Update security patches

2. **Monthly**
   - Database maintenance
   - Performance review
   - Backup verification

3. **Quarterly**
   - Security audit
   - Performance optimization
   - Dependency updates

## 📞 Support

For deployment support:
- **Documentation**: Check README.md
- **Issues**: GitHub Issues
- **Email**: support@airepublic.com
- **Emergency**: +1-XXX-XXX-XXXX

---

**Professional Deployment Complete! 🚀**
