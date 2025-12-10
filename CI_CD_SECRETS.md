# AI Republic CI/CD Secrets and Variables

This document outlines the necessary GitHub Actions secrets and Kubernetes secrets for deploying the AI Republic application to Hetzner Kubernetes via GitHub Actions.

## GitHub Actions Secrets (Required)

These secrets must be configured in your GitHub repository settings (`Settings > Secrets and variables > Actions`).

### Required Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `HETZNER_SSH_PRIVATE_KEY` | SSH private key for Hetzner server access | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Yes |
| `HETZNER_HOST` | Hetzner server IP address | `178.156.162.135` | Yes |
| `FLASK_SECRET_KEY` | Flask secret key for session security (generate with `openssl rand -hex 32`) | `a1b2c3d4e5f6...` | Yes |
| `POSTGRES_PASSWORD` | PostgreSQL database password | `your-secure-password-here` | Yes |

### Optional Secrets

| Secret Name | Description | Example Value | Required |
|------------|-------------|---------------|----------|
| `HETZNER_APP_URL` | Application URL for health checks | `https://airepubliq.com` | No |

## Kubernetes Secrets (Managed by CI/CD)

The CI/CD pipeline will automatically create or update Kubernetes Secrets in the `airepubliq` namespace:

### Secret: `postgres-secrets`
- `postgres-db`: Database name (`ai_refinement_v2`)
- `postgres-user`: Database user (`airepublic`)
- `postgres-password`: Database password (from GitHub Secrets)

### Secret: `backend-secrets`
- `flask-env`: Flask environment (`production`)
- `database-url`: PostgreSQL connection string
- `redis-url`: Redis connection string
- `secret-key`: Flask secret key (from GitHub Secrets)

## Setup Instructions

### 1. GitHub Actions Secrets

1. Go to your GitHub repository: https://github.com/janisrael/ai-republiq
2. Navigate to **Settings → Secrets and variables → Actions**
3. Click **New repository secret**
4. Add each secret listed above

### 2. Generate Flask Secret Key

```bash
openssl rand -hex 32
```

### 3. Generate PostgreSQL Password

Use a strong, random password:
```bash
openssl rand -base64 24
```

### 4. Verify Secrets

After adding secrets, verify they're set correctly:
- Go to **Settings → Secrets and variables → Actions**
- All secrets should be listed
- Values are hidden (showing only `••••••••`)

## Architecture

The application consists of:
- **Backend**: Flask API (Python) - Port 5001
- **Frontend**: Nginx serving static files (Node.js/Vite build) - Port 80
- **PostgreSQL**: Database - Port 5432
- **Redis**: Cache - Port 6379

## Deployment Process

1. Push to `main` branch triggers CI/CD
2. Tests run automatically
3. Docker images are built on Hetzner server (backend + frontend)
4. Images are imported into k3s
5. Kubernetes manifests are applied
6. Application is available at `https://airepubliq.com`

## Troubleshooting

### Secret Not Found Error
- Verify secret name matches exactly (case-sensitive)
- Check secret is added to the correct repository
- Ensure workflow has permission to read secrets

### Database Connection Failed
- Verify PostgreSQL password is correct in GitHub Secrets
- Check PostgreSQL StatefulSet is running: `kubectl get pods -n airepubliq -l app=postgres`
- Check PostgreSQL logs: `kubectl logs -n airepubliq -l app=postgres`

### Backend Not Starting
- Check backend logs: `kubectl logs -n airepubliq -l app=backend`
- Verify backend secrets are created: `kubectl get secrets -n airepubliq`
- Check database connectivity from backend pod

---

**Last Updated**: 2025-01-08  
**Maintained By**: Jan Francis Israel
