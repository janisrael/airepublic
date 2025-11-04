# AI Republic Dashboard - Professional Makefile
# Standardized commands for development and deployment

.PHONY: help install dev test lint format clean docker-build docker-up docker-down

# Default target
help: ## Show this help message
	@echo "AI Republic Dashboard - Professional Development Commands"
	@echo "========================================================"
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Development Setup

install: ## Install all dependencies
	@echo "📦 Installing dependencies..."
	pip install -r requirements-dev.txt
	cd frontend && npm install
	pre-commit install
	@echo "✅ Installation complete!"

install-prod: ## Install production dependencies only
	@echo "📦 Installing production dependencies..."
	pip install -r requirements.txt
	cd frontend && npm ci --only=production

##@ Development

dev: ## Start development servers (V2)
	@echo "🚀 Starting development servers..."
	./start_services.sh v2

dev-v1: ## Start V1 development servers
	@echo "🚀 Starting V1 development servers..."
	./start_services.sh v1

dev-all: ## Start all development servers (V1 + V2)
	@echo "🚀 Starting all development servers..."
	./start_services.sh all

stop: ## Stop all services
	@echo "🛑 Stopping all services..."
	./start_services.sh stop

##@ Code Quality

lint: ## Run linting checks
	@echo "🔍 Running linting checks..."
	flake8 backend/
	mypy backend/
	bandit -r backend/
	@echo "✅ Linting complete!"

format: ## Format code with black and isort
	@echo "🎨 Formatting code..."
	black backend/ frontend/src/
	isort backend/ frontend/src/
	@echo "✅ Formatting complete!"

format-check: ## Check code formatting without changes
	@echo "🔍 Checking code formatting..."
	black --check backend/ frontend/src/
	isort --check-only backend/ frontend/src/
	@echo "✅ Format check complete!"

##@ Testing

test: ## Run all tests
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=backend --cov-report=html --cov-report=term
	@echo "✅ Tests complete!"

test-unit: ## Run unit tests only
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v -m "not integration and not e2e"

test-integration: ## Run integration tests only
	@echo "🧪 Running integration tests..."
	pytest tests/integration/ -v -m integration

test-e2e: ## Run end-to-end tests
	@echo "🧪 Running E2E tests..."
	pytest tests/e2e/ -v -m e2e

test-watch: ## Run tests in watch mode
	@echo "🧪 Running tests in watch mode..."
	pytest tests/ -v --cov=backend -f

##@ Database

db-migrate: ## Run database migrations
	@echo "🗄️ Running database migrations..."
	cd backend && python -m alembic upgrade head

db-create: ## Create database tables
	@echo "🗄️ Creating database tables..."
	cd backend && python create_v2_tables.py

db-reset: ## Reset database (WARNING: Destructive)
	@echo "⚠️ Resetting database..."
	cd backend && python -c "import os; os.remove('ai_refinement_v2.db') if os.path.exists('ai_refinement_v2.db') else None"
	$(MAKE) db-create

##@ Docker

docker-build: ## Build Docker images
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-up: ## Start Docker services
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

docker-down: ## Stop Docker services
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "🐳 Showing Docker logs..."
	docker-compose logs -f

docker-clean: ## Clean Docker resources
	@echo "🧹 Cleaning Docker resources..."
	docker-compose down -v
	docker system prune -f

##@ Production

build: ## Build for production
	@echo "🏗️ Building for production..."
	$(MAKE) format-check
	$(MAKE) lint
	$(MAKE) test
	cd frontend && npm run build
	@echo "✅ Production build complete!"

deploy: ## Deploy to production (requires configuration)
	@echo "🚀 Deploying to production..."
	# Add deployment commands here
	@echo "✅ Deployment complete!"

##@ Monitoring

logs: ## Show application logs
	@echo "📋 Showing application logs..."
	tail -f backend/api_server_v2.log frontend/frontend.log

monitor: ## Start monitoring services
	@echo "📊 Starting monitoring services..."
	docker-compose up -d prometheus grafana
	@echo "📊 Prometheus: http://localhost:9090"
	@echo "📊 Grafana: http://localhost:3000 (admin/admin123)"

##@ Utilities

clean: ## Clean temporary files and caches
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/
	cd frontend && rm -rf node_modules/ dist/ .vite/
	@echo "✅ Cleanup complete!"

security: ## Run security checks
	@echo "🔒 Running security checks..."
	safety check
	bandit -r backend/ -f json -o bandit-report.json
	@echo "✅ Security checks complete!"

deps-update: ## Update dependencies
	@echo "🔄 Updating dependencies..."
	pip-compile requirements.in
	pip-compile requirements-dev.in
	cd frontend && npm update
	@echo "✅ Dependencies updated!"

##@ Documentation

docs: ## Generate documentation
	@echo "📚 Generating documentation..."
	cd docs && make html
	@echo "✅ Documentation generated!"

docs-serve: ## Serve documentation locally
	@echo "📚 Serving documentation..."
	cd docs/_build/html && python -m http.server 8000

##@ Performance

benchmark: ## Run performance benchmarks
	@echo "⚡ Running performance benchmarks..."
	pytest tests/benchmark/ -v --benchmark-only

load-test: ## Run load tests
	@echo "⚡ Running load tests..."
	locust -f tests/load/locustfile.py --host=http://localhost:5001

##@ Backup

backup: ## Create backup
	@echo "💾 Creating backup..."
	tar -czf backup-$(shell date +%Y%m%d_%H%M%S).tar.gz \
		--exclude=node_modules \
		--exclude=.git \
		--exclude=__pycache__ \
		--exclude=*.pyc \
		.
	@echo "✅ Backup created!"

##@ Status

status: ## Show system status
	@echo "📊 System Status"
	@echo "================"
	@echo "Backend V1: $$(curl -s http://localhost:5000/api/status > /dev/null && echo '✅ Running' || echo '❌ Stopped')"
	@echo "Backend V2: $$(curl -s http://localhost:5001/api/status > /dev/null && echo '✅ Running' || echo '❌ Stopped')"
	@echo "Frontend: $$(curl -s http://localhost:5173 > /dev/null && echo '✅ Running' || echo '❌ Stopped')"
	@echo "Redis: $$(redis-cli ping > /dev/null 2>&1 && echo '✅ Running' || echo '❌ Stopped')"
	@echo "PostgreSQL: $$(pg_isready -h localhost -p 5432 > /dev/null 2>&1 && echo '✅ Running' || echo '❌ Stopped')"
