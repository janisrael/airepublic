# AI Republic Dashboard

AI Model Management Platform - In Development

**Deployment**: Automated CI/CD via GitHub Actions to Hetzner Kubernetes | Last updated: 2025-01-08

**Live URL**: https://airepubliq.com

## Overview

AI Republic Dashboard is a platform for managing AI models, training pipelines, and deployment workflows. Built with modern architecture principles, it supports both local and cloud-based AI models with performance and scalability.

The platform enables users to manage multiple AI models, create and train custom models using LoRA fine-tuning, organize datasets, and deploy AI agents (Minions) with specialized capabilities (Spirits) for various tasks.

## Key Features

### Model Management
- Multi-Provider Model Support: Ollama, OpenAI, Anthropic, NVIDIA NIM, and custom models
- Model Registry: Centralized repository for all AI models
- Model Versioning: Track and manage model versions
- Model Performance Analytics: Monitor model usage and performance metrics

### Training & Fine-Tuning
- LoRA Fine-Tuning: Efficient parameter-efficient fine-tuning for custom models
- Training Pipeline Management: Create, monitor, and manage training jobs
- Dataset Management: Upload, organize, and manage training datasets
- Training Progress Tracking: Real-time WebSocket updates for training jobs
- Checkpoint Management: Save and restore training checkpoints

### Minion System
- AI Agent Creation: Create specialized AI agents (Minions) for specific tasks
- Minion Classes: Pre-configured spirit pathways for common use cases (Developer, Planner, Content Marketer, etc.)
- Level System: Minions gain experience and unlock new capabilities
- Spirit System: Dynamic AI agent configurations with specialized tools

### Advanced Features
- Authentication & Authorization: JWT-based authentication with role-based access control (RBAC)
- User Management: Comprehensive user profiles, avatars, and preferences
- Session Management: Redis-backed secure session handling
- Audit Logging: Track user actions and system events
- Rate Limiting: API protection and abuse prevention

### Performance & Scalability
- Redis Caching: Intelligent caching layer for improved performance
- Connection Pooling: Efficient database access with SQLAlchemy
- WebSocket Support: Real-time updates for training progress and notifications
- Horizontal Scaling: Kubernetes-ready architecture for production deployment

### User Interface
- Modern Neumorphism Design: Beautiful, responsive UI with dark mode support
- Real-Time Updates: WebSocket-based live updates for training and jobs
- Responsive Layout: Mobile-friendly interface
- Intuitive Navigation: Easy-to-use dashboard and management interfaces

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                                  │
│                                                                         │
│                    ┌──────────────────────┐                            │
│                    │   Frontend (Vue.js)  │                            │
│                    │   Nginx Static Files │                            │
│                    │   Port: 80           │                            │
│                    └──────────┬───────────┘                            │
│                               │                                         │
└───────────────────────────────┼─────────────────────────────────────────┘
                                │ HTTP/HTTPS                                
                                │                                           
┌───────────────────────────────▼─────────────────────────────────────────┐
│                         API LAYER                                       │
│                                                                         │
│                    ┌──────────────────────┐                            │
│                    │   Backend (Flask)    │                            │
│                    │   Port: 5001        │                            │
│                    │   Flask-SocketIO     │                            │
│                    └───────┬──────────────┘                            │
│                            │                                             │
└────────────────────────────┼─────────────────────────────────────────────┘
                             │                                               
        ┌────────────────────┼────────────────────┐                          
        │                    │                    │                          
        ▼                    ▼                    ▼                          
┌──────────────┐   ┌──────────────┐   ┌──────────────┐                      
│  PostgreSQL  │   │    Redis     │   │  ChromaDB    │                      
│  Port: 5432  │   │  Port: 6379  │   │  Vector DB   │                      
│              │   │              │   │              │                      
│  • Users     │   │  • Sessions  │   │  • RAG Data  │                      
│  • Models    │   │  • Cache     │   │  • Embeddings│                      
│  • Training  │   │  • Rate Limit│   │              │                      
│  • Minions   │   │              │   │              │                      
│  • Spirits   │   │              │   │              │                      
└──────────────┘   └──────────────┘   └──────────────┘                      
                                                                             
┌─────────────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES                                    │
│                                                                         │
│  • Ollama (Local LLM)      • OpenAI API      • Anthropic API          │
│  • NVIDIA NIM               • HuggingFace     • RunPod (GPU Training)  │
└─────────────────────────────────────────────────────────────────────────┘
```

### Component Details

**Frontend**: Vue.js application built with Vite, served via Nginx in production. Provides user interface for managing models, training jobs, datasets, and minions.

**Backend**: Flask REST API with WebSocket support (Flask-SocketIO) for real-time updates. Handles authentication, model management, training orchestration, and minion/spirit operations.

**PostgreSQL**: Primary relational database storing users, models, training jobs, datasets, minions, spirits, and system metadata.

**Redis**: Caching layer and session storage. Also used for rate limiting and real-time data.

**ChromaDB**: Vector database for RAG (Retrieval Augmented Generation) functionality, storing embeddings and enabling semantic search.

**External Services**: Integration with various AI model providers and cloud GPU services for training and inference.


### Backend
- Python 3.11
- Flask 2.3.3 - Web framework
- Flask-SocketIO 5.3.6 - WebSocket support
- SQLAlchemy 2.0.21 - Database ORM
- PostgreSQL 15 - Primary database
- Redis 7 - Caching and session storage
- PyTorch 2.0+ - Deep learning framework
- Transformers 4.30+ - HuggingFace model library
- PEFT 0.4+ - Parameter-Efficient Fine-Tuning (LoRA)
- ChromaDB - Vector database for RAG

### Frontend
- Vue.js 3 - Frontend framework
- Vite - Build tool and dev server
- Neumorphism UI - Design system
- WebSocket Client - Real-time updates

### Infrastructure
- Docker - Containerization
- Kubernetes (k3s) - Container orchestration
- Nginx Ingress Controller - HTTP/HTTPS routing
- GitHub Actions - CI/CD automation
- Hetzner Cloud - Cloud hosting

## Installation

### Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- PostgreSQL 12 or higher
- Redis 7 or higher
- Docker (optional, for containerized deployment)

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:janisrael/airepublic.git
   cd ai-refinement-dashboard
   ```

2. **Set up backend:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up frontend:**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure environment variables:**
   ```bash
   # Backend
   cp env.example .env
   # Edit .env with your configuration
   
   # Frontend
   cd frontend
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Set up database:**
   ```bash
   # Create PostgreSQL database
   createdb ai_refinement_v2
   
   # Run migrations (if available)
   # python backend/manage.py migrate
   ```

6. **Start services:**
   ```bash
   # Terminal 1: Start Redis
   redis-server
   
   # Terminal 2: Start backend
   cd backend
   python app_server_new.py
   
   # Terminal 3: Start frontend
   cd frontend
   npm run dev
   ```

7. **Access the application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5001
   - API Documentation: http://localhost:5001/api/docs

### Docker Setup

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Configuration

### Environment Variables

#### Backend (.env)
```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
BACKEND_PORT=5001

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/ai_refinement_v2

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# ChromaDB Configuration
CHROMADB_PATH=backend/chromadb_data

# Model Provider APIs (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
OLLAMA_BASE_URL=http://localhost:11434
```

#### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:5001
```

## Project Structure

```
ai-refinement-dashboard/
├── backend/
│   ├── app/
│   │   ├── routes/          # API route blueprints
│   │   ├── models/          # SQLAlchemy models
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utility functions
│   ├── migrations/         # Database migrations
│   ├── scripts/            # Utility scripts
│   ├── chromadb_data/      # ChromaDB vector store
│   ├── app_server_new.py   # Main Flask application
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/         # Page views
│   │   ├── assets/        # Static assets
│   │   └── config/        # Configuration
│   ├── public/            # Public assets
│   ├── package.json       # Node dependencies
│   └── vite.config.js     # Vite configuration
├── k8s/                   # Kubernetes manifests
├── docs/                  # Documentation
├── docker-compose.yml     # Docker Compose configuration
├── CI_CD_SECRETS.md      # CI/CD secrets documentation
└── README.md             # This file
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `GET /api/auth/me` - Get current user

### Models
- `GET /api/models` - List all models
- `POST /api/models` - Create new model
- `GET /api/models/{id}` - Get model details
- `PUT /api/models/{id}` - Update model
- `DELETE /api/models/{id}` - Delete model

### Training
- `GET /api/training/jobs` - List training jobs
- `POST /api/training/jobs` - Create training job
- `GET /api/training/jobs/{id}` - Get job details
- `GET /api/training/jobs/{id}/progress` - Get training progress (WebSocket)

### Datasets
- `GET /api/datasets` - List datasets
- `POST /api/datasets` - Upload dataset
- `GET /api/datasets/{id}` - Get dataset details
- `DELETE /api/datasets/{id}` - Delete dataset

### Minions
- `GET /api/minions` - List user minions
- `POST /api/minions` - Create minion
- `GET /api/minions/{id}` - Get minion details
- `PUT /api/minions/{id}` - Update minion
- `DELETE /api/minions/{id}` - Delete minion

## Database Schema

### Core Tables
- `users` - User accounts and authentication
- `roles` - Role definitions for RBAC
- `permissions` - Permission definitions
- `user_roles` - User-role assignments
- `models` - AI model configurations
- `training_jobs` - Training pipeline jobs
- `datasets` - Dataset metadata
- `minions` - AI agent configurations
- `spirits` - Dynamic spirit configurations
- `minion_classes` - Pre-configured minion classes

See `docs/DATABASE_ERD.md` for detailed database schema documentation.

## Production Deployment

### Kubernetes Deployment

The application is deployed to Hetzner Kubernetes (k3s) using GitHub Actions CI/CD.

**Architecture:**
- Namespace: `airepubliq`
- PostgreSQL StatefulSet with PersistentVolumeClaim (10Gi)
- Redis Deployment
- Backend Deployment (2 replicas) with PVCs for ChromaDB and logs
- Frontend Deployment (2 replicas) serving static files via Nginx
- Ingress for external access

**Deployment Process:**
1. Push to `main` branch triggers CI/CD
2. Tests run automatically
3. Docker images are built on Hetzner server (backend + frontend)
4. Images are imported into k3s
5. Kubernetes manifests are applied
6. Application is available at `https://airepubliq.com`

**Required GitHub Secrets:**
- `HETZNER_SSH_PRIVATE_KEY` - SSH key for server access
- `HETZNER_HOST` - Hetzner server IP address
- `FLASK_SECRET_KEY` - Flask secret key for sessions
- `POSTGRES_PASSWORD` - PostgreSQL database password

See `CI_CD_SECRETS.md` for detailed setup instructions.

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

### Code Quality

```bash
# Linting
flake8 backend/
eslint frontend/src/

# Formatting
black backend/
prettier frontend/src/
```

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- `docs/ARCHITECTURAL_PLAN/` - System architecture and design
- `docs/AMIGO_*.md` - Amigo model training documentation
- `docs/DATABASE_ERD.md` - Database entity relationship diagram
- `SETUP.md` - Detailed setup guide
- `CI_CD_SECRETS.md` - CI/CD configuration guide

## Security

### Authentication & Authorization
- JWT-based stateless authentication
- Role-Based Access Control (RBAC)
- Session management with Redis
- Password hashing with bcrypt

### Security Features
- Input validation with Pydantic models
- SQL injection protection via SQLAlchemy ORM
- XSS protection with content sanitization
- CSRF protection with token validation
- Rate limiting for API endpoints

## Performance

### Optimization Features
- Redis caching for frequently accessed data
- Database connection pooling
- Lazy loading for large datasets
- Gzip compression for API responses
- CDN-ready static asset optimization

### Benchmarks
- API Response Time: < 100ms (cached)
- Database Queries: < 50ms (pooled)
- Concurrent Users: 1000+ (tested)
- Memory Usage: < 512MB per service

## Troubleshooting

### Common Issues

**Database Connection Failed:**
- Verify PostgreSQL is running: `systemctl status postgresql`
- Check connection string in `.env`
- Verify database exists: `psql -l`

**Redis Connection Failed:**
- Verify Redis is running: `redis-cli ping`
- Check Redis URL in `.env`
- Verify Redis port is accessible

**Training Jobs Not Starting:**
- Check GPU availability (if using GPU)
- Verify dataset paths are correct
- Check training logs: `kubectl logs -n airepubliq -l app=backend`

**Frontend Not Loading:**
- Verify backend API is accessible
- Check CORS configuration
- Verify API base URL in frontend `.env`

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make changes and test: `make test`
4. Commit changes: `git commit -m 'Add amazing feature'`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open Pull Request

### Code Standards
- Python: Black formatting, type hints with MyPy
- JavaScript: ESLint, Prettier
- Tests: 90%+ coverage required
- Documentation: Docstrings for all functions

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

**Created By**: Jan Francis Israel  
**Website**: https://janisrael.com  
**HuggingFace**: https://huggingface.co/swordfish7412  
**GitHub**: https://github.com/janisrael/airepublic

---

**Project**: AI Republic Dashboard  
**Version**: 2.0.0  
**Status**: Production Ready  
**Last Updated**: January 2025
