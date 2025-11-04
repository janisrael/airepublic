# AWS EC2 Setup Guide - AI Refinement Dashboard

## 📊 Instance Type Comparison

### For Accounts Created After July 15, 2025 (Free Tier Eligible)

#### Option 1: c7i-flex.large (Compute-Optimized)
- **vCPU**: 2 cores
- **RAM**: 4 GiB (4096 MB)
- **Network**: Up to 10 Gbps
- **Purpose**: High-performance computing, CPU-intensive workloads
- **Free Tier**: 750 hours/month for 6 months
- **After Free Tier**: ~$68/month

#### Option 2: m7i-flex.large (General-Purpose) ⭐ **RECOMMENDED**
- **vCPU**: 2 cores
- **RAM**: 8 GiB (8192 MB) - **DOUBLE the RAM**
- **Network**: Up to 10 Gbps
- **Purpose**: General-purpose, balanced compute and memory
- **Free Tier**: 750 hours/month for 6 months
- **After Free Tier**: ~$70/month

### Comparison for Your Setup

| Feature | c7i-flex.large | m7i-flex.large | Winner |
|---------|---------------|----------------|--------|
| **CPU** | 2 vCPU | 2 vCPU | Tie |
| **RAM** | 4 GB | **8 GB** | ⭐ m7i-flex.large |
| **Price** | ~$68/month | ~$70/month | c7i-flex.large (slight) |
| **Your RAM Usage** | ~1.64GB (fits) | ~1.64GB (plenty of room) | ⭐ m7i-flex.large |
| **PostgreSQL** | Tight | Comfortable | ⭐ m7i-flex.large |
| **Scalability** | Limited | Better | ⭐ m7i-flex.large |
| **Workload Type** | Compute-heavy | **General-purpose** | ⭐ m7i-flex.large |

### 🎯 **Recommendation: m7i-flex.large**

**Why m7i-flex.large is better for your setup:**
1. ✅ **8GB RAM vs 4GB** - Your setup uses ~1.64GB, giving you 6GB+ headroom for growth
2. ✅ **General-purpose** - Perfect for PostgreSQL + Flask + Frontend mixed workload
3. ✅ **Better for databases** - More RAM helps PostgreSQL performance significantly
4. ✅ **Future-proof** - Room to add Redis, increase database size, handle more users
5. ✅ **Only $2/month more** after free tier - worth it for 2x RAM

**Use c7i-flex.large only if:**
- You're doing heavy CPU-intensive processing (you're not - using external models)
- You're on a strict budget after free tier
- You know your RAM usage will stay below 3GB long-term

---

## 🚀 Step-by-Step EC2 Setup Guide

### Step 1: Prepare AWS Account

1. **Sign in to AWS Console**
   - Go to https://console.aws.amazon.com
   - Sign in with your AWS account

2. **Check Free Tier Eligibility**
   - Navigate to: AWS Console → Billing & Cost Management → Free Tier
   - Verify your account is eligible (new accounts get 6 months of free tier for newer instance types)

### Step 2: Launch EC2 Instance

1. **Navigate to EC2 Dashboard**
   - AWS Console → Services → EC2
   - Click "Launch Instance" button

2. **Name Your Instance**
   - Name: `ai-refinement-dashboard`
   - (Optional) Add tags: Environment=Production, Project=AI-Republic

### Step 3: Choose AMI (Amazon Machine Image)

**Recommended: Ubuntu 22.04 LTS**
- Click "Browse more AMIs"
- Search for: `ubuntu`
- Select: **Ubuntu Server 22.04 LTS** (64-bit x86)
- Architecture: `x86_64`
- **Why Ubuntu**: Better Python/Node.js support, familiar package manager

**Alternative**: Amazon Linux 2023 (if you prefer AWS-optimized)

### Step 4: Choose Instance Type

1. **Click "Edit" next to Instance type**
2. **Filter**: Select "Free tier eligible" if available
3. **Recommended**: Select **m7i-flex.large** (or t3.micro if m7i-flex not available)
   - If m7i-flex.large is not showing:
     - Remove "Free tier" filter
     - Search for "m7i-flex.large"
     - **Note**: Verify your account qualifies for this free tier option

### Step 5: Create or Select Key Pair

1. **Key pair name**: `ai-refinement-keypair` (or your preferred name)
2. **Key pair type**: RSA
3. **Private key file format**: `.pem` (for OpenSSH)
4. **Click "Create key pair"**
5. **IMPORTANT**: Download and save the `.pem` file securely
   - This is your ONLY way to SSH into the instance
   - Store it in `~/.ssh/` on your local machine
   - Set permissions: `chmod 400 ~/.ssh/ai-refinement-keypair.pem`

### Step 6: Network Settings

1. **VPC**: Leave default (or create new VPC if needed)
2. **Subnet**: Leave default
3. **Auto-assign Public IP**: Enable
4. **Security Group**: Create new security group
   - **Security group name**: `ai-refinement-sg`
   - **Description**: Security group for AI Refinement Dashboard

5. **Add Inbound Rules**:
   ```
   Type           Protocol    Port Range    Source
   ─────────────────────────────────────────────────────
   SSH            TCP         22             My IP (or 0.0.0.0/0 for development)
   HTTP           TCP         80             0.0.0.0/0
   HTTPS          TCP         443            0.0.0.0/0
   Custom TCP     TCP         5001           0.0.0.0/0 (Backend API)
   Custom TCP     TCP         5173           0.0.0.0/0 (Frontend Dev - optional)
   ```

   **⚠️ Security Note**: For production, restrict SSH (port 22) to your IP only

### Step 7: Configure Storage

1. **Volume type**: General Purpose SSD (gp3)
2. **Size**: 30 GB (Free Tier limit)
3. **Delete on termination**: ✅ Enabled (or disable if you want to keep data)
4. **Encrypted**: Optional (recommended for production)

### Step 8: Advanced Details (Optional)

**User data script** (Paste this in "Advanced details" → "User data"):
```bash
#!/bin/bash
# Update system
apt-get update -y
apt-get upgrade -y

# Install essential tools
apt-get install -y git curl wget build-essential

# Set timezone
timedatectl set-timezone UTC

# Enable automatic security updates
apt-get install -y unattended-upgrades
```

### Step 9: Review and Launch

1. **Review configuration**:
   - Instance type: m7i-flex.large (or t3.micro)
   - Storage: 30 GB
   - Security groups: Configured
   - Key pair: Created and downloaded

2. **Click "Launch instance"**

3. **Wait for instance to start** (1-2 minutes)
   - Status will change from "pending" to "running"
   - Note the **Public IPv4 address** (you'll need this)

---

## 📡 Step 10: Connect to Your Instance

### Option A: Using SSH (Linux/Mac)

```bash
# 1. Navigate to key location
cd ~/.ssh

# 2. Set permissions (IMPORTANT - SSH won't work without this)
chmod 400 ai-refinement-keypair.pem

# 3. Connect to instance (replace with your Public IP)
ssh -i ai-refinement-keypair.pem ubuntu@<YOUR-PUBLIC-IP>
```

### Option B: Using AWS Systems Manager Session Manager

1. Install AWS CLI and Session Manager plugin
2. Use AWS Console → EC2 → Connect → Session Manager

### Option C: Using EC2 Instance Connect (Browser)

1. AWS Console → EC2 → Select instance
2. Click "Connect" → "EC2 Instance Connect"
3. Click "Connect" (opens browser-based terminal)

---

## 🛠️ Step 11: Initial Server Setup

Once connected, run these commands:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install essential tools
sudo apt install -y \
    git \
    curl \
    wget \
    build-essential \
    software-properties-common \
    ca-certificates \
    gnupg \
    lsb-release

# 3. Install Python 3.10+ (Ubuntu 22.04 comes with Python 3.10)
python3 --version  # Verify version

# 4. Install pip
sudo apt install -y python3-pip python3-venv

# 5. Install Node.js 18+ (using NodeSource repository)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
node --version  # Verify version (should be v18+)
npm --version

# 6. Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql

# 7. Configure PostgreSQL for low memory usage
sudo nano /etc/postgresql/*/main/postgresql.conf

# Add/modify these lines:
# shared_buffers = 128MB
# effective_cache_size = 256MB
# maintenance_work_mem = 64MB
# work_mem = 4MB

# 8. Restart PostgreSQL
sudo systemctl restart postgresql

# 9. Set up PostgreSQL database and user
sudo -u postgres psql << EOF
CREATE DATABASE ai_republic_spirits;
CREATE USER ai_republic WITH ENCRYPTED PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE ai_republic_spirits TO ai_republic;
ALTER USER ai_republic CREATEDB;
\q
EOF

# 10. Install Nginx (for serving frontend and reverse proxy)
sudo apt install -y nginx

# 11. Install Git (if not already installed)
sudo apt install -y git

# 12. Configure firewall (UFW)
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow 5001/tcp # Backend API
sudo ufw enable

# 13. Set up swap space (2GB - helps with memory constraints)
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 14. Verify everything
python3 --version
node --version
npm --version
sudo systemctl status postgresql
sudo systemctl status nginx
```

---

## 📦 Step 12: Deploy Your Application

```bash
# 1. Clone your repository
cd ~
git clone <YOUR-REPO-URL> ai-refinement-dashboard
cd ai-refinement-dashboard

# 2. Set up backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Set up frontend
cd ../frontend
npm install

# 4. Build frontend for production
npm run build

# 5. Create .env file
cd ..
cp env.example .env

# Edit .env with your settings:
nano .env
```

**Update `.env` file with production settings:**
```env
# Production Settings
DEBUG_MODE=false
AUTO_RELOAD=false
FLASK_ENV=production

# Database (use localhost since PostgreSQL is on same instance)
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_DB=ai_republic_spirits
POSTGRES_USER=ai_republic
POSTGRES_PASSWORD=your-secure-password-here

# Backend
BACKEND_PORT=5001
BACKEND_HOST=0.0.0.0

# Frontend API URL (update with your EC2 public IP or domain)
VITE_API_BASE_URL=http://<YOUR-EC2-IP>:5001/api/v2

# Skip Redis for free tier
# REDIS_HOST=
# REDIS_PORT=
```

---

## 🔧 Step 13: Configure Nginx

```bash
# Create Nginx configuration
sudo nano /etc/nginx/sites-available/ai-refinement

# Paste this configuration:
```

```nginx
server {
    listen 80;
    server_name <YOUR-DOMAIN-OR-IP>;

    # Frontend static files
    location / {
        root /home/ubuntu/ai-refinement-dashboard/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # Backend API proxy
    location /api {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support (for training updates)
    location /socket.io {
        proxy_pass http://127.0.0.1:5001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/ai-refinement /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default  # Remove default site

# Test configuration
sudo nginx -t

# Reload Nginx
sudo systemctl reload nginx
```

---

## 🚀 Step 14: Run Application as Service

### Create Backend Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/ai-refinement-backend.service
```

**Paste this:**
```ini
[Unit]
Description=AI Refinement Dashboard Backend
After=network.target postgresql.service

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-refinement-dashboard/backend
Environment="PATH=/home/ubuntu/ai-refinement-dashboard/backend/venv/bin"
ExecStart=/home/ubuntu/ai-refinement-dashboard/backend/venv/bin/python app_server_new.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable ai-refinement-backend
sudo systemctl start ai-refinement-backend

# Check status
sudo systemctl status ai-refinement-backend

# View logs
sudo journalctl -u ai-refinement-backend -f
```

---

## ✅ Step 15: Verify Deployment

```bash
# 1. Check backend is running
curl http://localhost:5001/health
curl http://localhost:5001/api/status

# 2. Check frontend is served
curl http://localhost

# 3. Check PostgreSQL
sudo -u postgres psql -d ai_republic_spirits -c "SELECT version();"

# 4. Check all services
sudo systemctl status ai-refinement-backend
sudo systemctl status nginx
sudo systemctl status postgresql

# 5. Check memory usage
free -h

# 6. Check disk usage
df -h
```

---

## 🔒 Step 16: Security Hardening (Recommended)

```bash
# 1. Update SSH configuration (disable password authentication)
sudo nano /etc/ssh/sshd_config

# Ensure these lines exist:
# PasswordAuthentication no
# PubkeyAuthentication yes

sudo systemctl restart sshd

# 2. Set up fail2ban (protect against brute force)
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# 3. Configure automatic security updates
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📊 Step 17: Monitoring Setup

```bash
# 1. Install CloudWatch agent (optional)
wget https://s3.amazonaws.com/amazoncloudwatch-agent/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb

# 2. Set up basic monitoring
# Monitor: CPU, Memory, Disk, Network
```

---

## 🎯 Quick Reference

### Instance Types Summary

| Instance Type | vCPU | RAM | Best For | Free Tier |
|--------------|------|-----|----------|-----------|
| **t3.micro** | 1 | 1 GB | Development/testing | ✅ 12 months |
| **m7i-flex.large** ⭐ | 2 | 8 GB | **Your production setup** | ✅ 6 months |
| c7i-flex.large | 2 | 4 GB | CPU-heavy workloads | ✅ 6 months |

### Important URLs

- **Backend API**: http://<YOUR-IP>:5001/api/status
- **Frontend**: http://<YOUR-IP>
- **Health Check**: http://<YOUR-IP>:5001/health

### Useful Commands

```bash
# View backend logs
sudo journalctl -u ai-refinement-backend -f

# Restart backend
sudo systemctl restart ai-refinement-backend

# Check service status
sudo systemctl status ai-refinement-backend nginx postgresql

# View resource usage
htop  # Install: sudo apt install htop

# Check disk space
df -h

# Check memory
free -h
```

---

## 🚨 Troubleshooting

### Backend won't start
```bash
# Check logs
sudo journalctl -u ai-refinement-backend -n 50

# Check if port is in use
sudo lsof -i :5001

# Test PostgreSQL connection
sudo -u postgres psql -d ai_republic_spirits
```

### Out of memory
```bash
# Check memory usage
free -h
top

# Increase swap if needed
sudo swapon --show
```

### Can't access from browser
```bash
# Check security group rules
# AWS Console → EC2 → Security Groups → ai-refinement-sg

# Check firewall
sudo ufw status

# Check Nginx
sudo nginx -t
sudo systemctl status nginx
```

---

## 📝 Next Steps

1. ✅ Set up domain name (optional - Route 53)
2. ✅ Configure SSL certificate (Let's Encrypt with Certbot)
3. ✅ Set up automated backups
4. ✅ Configure CloudWatch alarms
5. ✅ Set up CI/CD pipeline

---

**Last Updated**: 2025-11-01  
**Recommended Instance**: **m7i-flex.large** (8GB RAM)  
**Author**: Agimat (Swordfish Project)

