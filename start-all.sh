#!/bin/bash

# Master Startup Script for BioMedical Intelligence Platform
# This script starts all components in the correct order

set -e  # Exit on error

echo "🚀 BioMedical Intelligence Platform - Master Startup"
echo "===================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker not found. Please install Docker first."
    exit 1
fi
print_success "Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose not found. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose found"

# Check Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 not found. Please install Python 3.9+ first."
    exit 1
fi
print_success "Python 3 found"

# Check Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js not found. Please install Node.js 18+ first."
    exit 1
fi
print_success "Node.js found"

echo ""

# Step 1: Start Infrastructure
echo "🐳 Step 1: Starting Infrastructure Services..."
cd infrastructure

if docker-compose ps 2>/dev/null | grep -q "Up"; then
    print_info "Infrastructure services already running"
else
    print_info "Starting PostgreSQL, Prometheus, Grafana..."
    docker-compose up -d
    sleep 5  # Wait for services to start
fi

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
for i in {1..30}; do
    if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_success "PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start"
        exit 1
    fi
    sleep 1
done

cd ..
echo ""

# Step 2: Setup Backend
echo "🔧 Step 2: Setting up Backend..."
cd auth-dashboard-service/backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if ! python -c "import fastapi" 2>/dev/null; then
    print_info "Installing backend dependencies..."
    pip install -q -r requirements.txt
    print_success "Backend dependencies installed"
else
    print_success "Backend dependencies already installed"
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cp .env.example .env
    print_success ".env file created"
fi

cd ../..
echo ""

# Step 3: Setup Frontend
echo "⚛️  Step 3: Setting up Frontend..."
cd auth-dashboard-service/frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_info "Installing frontend dependencies..."
    npm install --silent
    print_success "Frontend dependencies installed"
else
    print_success "Frontend dependencies already installed"
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    print_info "Creating .env.local file..."
    cp .env.local.example .env.local
    print_success ".env.local file created"
fi

cd ../..
echo ""

# Step 4: Show startup instructions
echo "✅ Setup Complete!"
echo ""
echo "===================================================="
echo "🎯 Next Steps: Start the Services"
echo "===================================================="
echo ""
echo "Open 2 separate terminal windows and run:"
echo ""
echo "Terminal 1 - Backend:"
echo "  cd auth-dashboard-service/backend"
echo "  source venv/bin/activate"
echo "  python app/main.py"
echo ""
echo "Terminal 2 - Frontend:"
echo "  cd auth-dashboard-service/frontend"
echo "  npm run dev"
echo ""
echo "===================================================="
echo "📊 Access URLs:"
echo "===================================================="
echo ""
echo "  Frontend Dashboard:  http://localhost:3000"
echo "  Backend API Docs:    http://localhost:8100/docs"
echo "  Backend Health:      http://localhost:8100/health"
echo ""
echo "===================================================="
echo "📚 Quick Test:"
echo "===================================================="
echo ""
echo "After starting services, visit:"
echo "  http://localhost:3000"
echo ""
echo "You will be redirected to login page."
echo "Click 'Sign up' to create your first account!"
echo ""
echo "🎉 Happy coding!"
