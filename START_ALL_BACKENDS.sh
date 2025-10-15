#!/bin/bash
# Start All Backend Services for Biomedical Intelligence Platform

set -e

echo "🚀 Starting Biomedical Platform Backend Services..."
echo ""

BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$BASE_DIR"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1 ; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start a Node.js backend
start_node_backend() {
    local service_name=$1
    local service_dir=$2
    local port=$3

    echo -e "${BLUE}=== Starting $service_name on port $port ===${NC}"

    if check_port $port; then
        echo -e "${YELLOW}⚠️  Port $port already in use, skipping $service_name${NC}"
        return 0
    fi

    cd "$BASE_DIR/$service_dir"

    # Ensure dependencies are installed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing dependencies..."
        npm install --quiet
    fi

    # Create/update .env file
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file..."
        cat > .env <<EOF
NODE_ENV=development
PORT=$port
DEMO_MODE=true
DATABASE_URL=demo-mode
REDIS_URL=demo-mode
CORS_ORIGINS=http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004,http://localhost:3005,http://localhost:3006
JWT_SECRET=demo-jwt-secret-key-$service_name
LOG_LEVEL=info
EOF
    fi

    # Start in background
    echo "🔄 Starting $service_name..."
    nohup npm run dev > /dev/null 2>&1 &
    local pid=$!

    # Wait a bit and check if it started
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name started successfully (PID: $pid)${NC}"
    else
        echo -e "${YELLOW}⚠️  $service_name may have failed to start${NC}"
    fi

    echo ""
}

# Function to start a Python backend
start_python_backend() {
    local service_name=$1
    local service_dir=$2
    local port=$3

    echo -e "${BLUE}=== Starting $service_name on port $port ===${NC}"

    if check_port $port; then
        echo -e "${YELLOW}⚠️  Port $port already in use, skipping $service_name${NC}"
        return 0
    fi

    cd "$BASE_DIR/$service_dir"

    # Check if venv exists
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv
    fi

    # Activate venv and install dependencies
    source venv/bin/activate

    if [ ! -f "venv/installed" ]; then
        echo "📦 Installing Python dependencies..."
        pip install -q -r requirements.txt
        touch venv/installed
    fi

    # Create/update .env file
    if [ ! -f ".env" ]; then
        echo "📝 Creating .env file..."
        cat > .env <<EOF
PORT=$port
ENVIRONMENT=development
DEMO_MODE=true
DATABASE_URL=demo-mode
REDIS_URL=demo-mode
CORS_ORIGINS=["http://localhost:3000","http://localhost:3001","http://localhost:3002","http://localhost:3003","http://localhost:3004","http://localhost:3005","http://localhost:3006"]
LOG_LEVEL=info
EOF
    fi

    # Start in background
    echo "🔄 Starting $service_name..."
    nohup uvicorn app.main:app --host 0.0.0.0 --port $port --reload > /dev/null 2>&1 &
    local pid=$!

    # Wait and check
    sleep 3
    if ps -p $pid > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name started successfully (PID: $pid)${NC}"
    else
        echo -e "${YELLOW}⚠️  $service_name may have failed to start${NC}"
    fi

    deactivate
    echo ""
}

echo "📋 Backend Services to Start:"
echo "  1. AI Diagnostics (Node.js) - Port 5001"
echo "  2. Medical Imaging AI (Python) - Port 5002"
echo "  3. Biosensing (Node.js) - Port 5003"
echo "  4. HIPAA Compliance (Node.js) - Port 5004"
echo "  5. BioTensor Labs (Python) - Port 5005"
echo "  6. MYNX NatalCare (Node.js) - Port 5006"
echo ""
read -p "Press Enter to continue..."

# Start Node.js backends
start_node_backend "AI Diagnostics" "ai-diagnostics/backend" 5001
start_node_backend "Biosensing" "biosensing/backend" 5003
start_node_backend "HIPAA Compliance" "hipaa-compliance/backend" 5004
start_node_backend "MYNX NatalCare" "mynx-natalcare/backend" 5006

# Start Python backends
start_python_backend "Medical Imaging AI" "medical-imaging-ai/backend" 5002
start_python_backend "BioTensor Labs" "biotensor-labs/backend" 5005

echo ""
echo -e "${GREEN}🎉 All backend services started!${NC}"
echo ""
echo "📊 Backend Status:"
echo "  AI Diagnostics:     http://localhost:5001/health"
echo "  Medical Imaging AI: http://localhost:5002/health"
echo "  Biosensing:         http://localhost:5003/health"
echo "  HIPAA Compliance:   http://localhost:5004/health"
echo "  BioTensor Labs:     http://localhost:5005/health"
echo "  MYNX NatalCare:     http://localhost:5006/health"
echo ""
echo "💡 To stop all services, run: ./STOP_ALL_BACKENDS.sh"
echo ""
