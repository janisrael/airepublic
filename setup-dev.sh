#!/bin/bash

# AI Republic Dashboard - Professional Development Setup
# This script sets up a complete professional development environment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}========================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}========================================${NC}"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check system requirements
check_requirements() {
    print_header "🔍 Checking System Requirements"
    
    local missing_deps=()
    
    # Check Python
    if command_exists python3; then
        local python_version=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        print_success "Python $python_version found"
    else
        missing_deps+=("python3")
    fi
    
    # Check Node.js
    if command_exists node; then
        local node_version=$(node --version)
        print_success "Node.js $node_version found"
    else
        missing_deps+=("node")
    fi
    
    # Check npm
    if command_exists npm; then
        local npm_version=$(npm --version)
        print_success "npm $npm_version found"
    else
        missing_deps+=("npm")
    fi
    
    # Check Redis
    if command_exists redis-server; then
        print_success "Redis server found"
    else
        missing_deps+=("redis-server")
    fi
    
    # Check PostgreSQL (optional)
    if command_exists psql; then
        print_success "PostgreSQL client found"
    else
        print_warning "PostgreSQL client not found (optional)"
    fi
    
    # Check Docker (optional)
    if command_exists docker; then
        print_success "Docker found"
    else
        print_warning "Docker not found (optional for containerized development)"
    fi
    
    # Check Git
    if command_exists git; then
        print_success "Git found"
    else
        missing_deps+=("git")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing required dependencies: ${missing_deps[*]}"
        print_status "Please install missing dependencies and run this script again"
        exit 1
    fi
    
    print_success "All system requirements satisfied!"
}

# Function to setup Python environment
setup_python() {
    print_header "🐍 Setting up Python Environment"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        print_status "Creating Python virtual environment..."
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_status "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    print_status "Activating virtual environment..."
    source venv/bin/activate
    
    # Upgrade pip
    print_status "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_status "Installing Python dependencies..."
    pip install -r requirements-dev.txt
    
    print_success "Python environment setup complete!"
}

# Function to setup Node.js environment
setup_nodejs() {
    print_header "📦 Setting up Node.js Environment"
    
    # Install frontend dependencies
    print_status "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    
    print_success "Node.js environment setup complete!"
}

# Function to setup environment configuration
setup_environment() {
    print_header "⚙️ Setting up Environment Configuration"
    
    # Copy environment file if it doesn't exist
    if [ ! -f ".env" ]; then
        print_status "Creating .env file from template..."
        cp env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file with your configuration"
    else
        print_status ".env file already exists"
    fi
    
    print_success "Environment configuration setup complete!"
}

# Function to setup pre-commit hooks
setup_pre_commit() {
    print_header "🪝 Setting up Pre-commit Hooks"
    
    if [ -f ".pre-commit-config.yaml" ]; then
        print_status "Installing pre-commit hooks..."
        pre-commit install
        print_success "Pre-commit hooks installed"
    else
        print_warning "Pre-commit configuration not found, skipping..."
    fi
}

# Function to setup database
setup_database() {
    print_header "🗄️ Setting up Database"
    
    # Create database tables
    print_status "Creating database tables..."
    cd backend
    python create_v2_tables.py
    cd ..
    
    print_success "Database setup complete!"
}

# Function to setup Redis
setup_redis() {
    print_header "🔴 Setting up Redis"
    
    # Check if Redis is running
    if redis-cli ping >/dev/null 2>&1; then
        print_success "Redis is running"
    else
        print_warning "Redis is not running, please start Redis server"
        print_status "On Ubuntu/Debian: sudo systemctl start redis-server"
        print_status "On macOS: brew services start redis"
        print_status "Or manually: redis-server"
    fi
}

# Function to run initial tests
run_tests() {
    print_header "🧪 Running Initial Tests"
    
    print_status "Running unit tests..."
    if pytest tests/unit/ -v --tb=short; then
        print_success "Unit tests passed!"
    else
        print_warning "Some unit tests failed, but setup can continue"
    fi
}

# Function to show next steps
show_next_steps() {
    print_header "🚀 Setup Complete - Next Steps"
    
    echo -e "${CYAN}Your professional development environment is ready!${NC}"
    echo ""
    echo -e "${YELLOW}Available Commands:${NC}"
    echo -e "  ${GREEN}make dev${NC}          - Start development servers (V2)"
    echo -e "  ${GREEN}make dev-v1${NC}       - Start V1 development servers"
    echo -e "  ${GREEN}make test${NC}         - Run all tests"
    echo -e "  ${GREEN}make lint${NC}         - Run code linting"
    echo -e "  ${GREEN}make format${NC}       - Format code"
    echo -e "  ${GREEN}make docker-up${NC}    - Start with Docker"
    echo ""
    echo -e "${YELLOW}Access Points:${NC}"
    echo -e "  ${GREEN}Frontend:${NC}         http://localhost:5173"
    echo -e "  ${GREEN}Backend V2:${NC}       http://localhost:5001"
    echo -e "  ${GREEN}API Docs:${NC}         http://localhost:5001/docs"
    echo -e "  ${GREEN}Monitoring:${NC}       make monitor"
    echo ""
    echo -e "${YELLOW}Development Tips:${NC}"
    echo -e "  • Edit ${GREEN}.env${NC} file for configuration"
    echo -e "  • Use ${GREEN}make help${NC} for all available commands"
    echo -e "  • Check ${GREEN}README.md${NC} for detailed documentation"
    echo -e "  • Run ${GREEN}make status${NC} to check service status"
    echo ""
    echo -e "${PURPLE}Happy coding! 🎉${NC}"
}

# Main setup function
main() {
    print_header "🚀 AI Republic Dashboard - Professional Setup"
    
    # Check system requirements
    check_requirements
    
    # Setup environments
    setup_python
    setup_nodejs
    setup_environment
    
    # Setup development tools
    setup_pre_commit
    
    # Setup services
    setup_redis
    setup_database
    
    # Run initial tests
    run_tests
    
    # Show next steps
    show_next_steps
}

# Run main function
main "$@"
