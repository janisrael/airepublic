#!/bin/bash

# Backup script for ai-refinement-dashboard
# Excludes unnecessary files like node_modules, dist, cache, etc.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$PROJECT_ROOT/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ai-refinement-dashboard_backup_${TIMESTAMP}"

echo "📦 Creating backup: $BACKUP_NAME"
echo "📂 Source: $SCRIPT_DIR"
echo "💾 Destination: $BACKUP_DIR"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create temporary exclude file
EXCLUDE_FILE=$(mktemp)
cat > "$EXCLUDE_FILE" << 'EOF'
# Node modules
node_modules/
**/node_modules/

# Build outputs
dist/
**/dist/
build/
**/build/
*.log
*.pid

# Cache directories
.cache/
.cache/**
.npm/
.yarn/
.vite/
__pycache__/
**/__pycache__/
*.pyc
*.pyo
*.pyd

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store
*.sublime-project
*.sublime-workspace

# Environment and secrets
.env
.env.local
.env.*.local
*.key
*.pem
*.p12

# Database files
*.db
*.sqlite
*.sqlite3

# OS files
Thumbs.db
desktop.ini

# Temporary files
*.tmp
*.temp
*.bak
*.backup
*.old

# Package manager lock files (optional - uncomment if you don't want them)
# package-lock.json
# yarn.lock
# pnpm-lock.yaml

# Git (optional - uncomment if you don't want .git)
# .git/
# .gitignore

# Docker volumes and data
docker-data/
volumes/

# Large binary files (only exclude if not needed)
# *.bin
# *.pickle
# *.pkl

# Database dumps and backups
*.sql
*.dump

# Large data directories
backend/app/services/chromadb_data/*
!backend/app/services/chromadb_data/.gitkeep

# Log files
*.log.*
logs/
*.log

# Documentation build outputs
docs/_build/
docs/.vuepress/dist/

# Test coverage
coverage/
.nyc_output/

# Monitoring data
monitoring/prometheus/data/
monitoring/grafana/data/
EOF

echo ""
echo "🔄 Starting backup (this may take a while)..."

# Use tar with exclude patterns
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
  --exclude-from="$EXCLUDE_FILE" \
  --exclude="backups" \
  --exclude="*.tar.gz" \
  -C "$PROJECT_ROOT" \
  "ai-refinement-dashboard" 2>/dev/null

# Clean up temp file
rm "$EXCLUDE_FILE"

# Check if backup was successful
if [ -f "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)
    echo ""
    echo "✅ Backup created successfully!"
    echo "📊 Size: $BACKUP_SIZE"
    echo "💾 Location: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
    
    # List last 5 backups
    echo ""
    echo "📋 Recent backups:"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null | tail -5 | awk '{print "  " $9 " (" $5 ")"}'
else
    echo ""
    echo "❌ Backup failed!"
    exit 1
fi

