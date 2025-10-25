#!/bin/bash

# Unified Deployment Script for Biomedical Intelligence Platform
# Deploys ALL services: Phase 1 (Core), Phase 2 (MVP), Phase 4 (Additional)

set -e  # Exit on error

echo "=========================================="
echo "Biomedical Intelligence Platform"
echo "Unified Deployment Script"
echo "=========================================="
echo ""

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SERVICES_STATUS=()

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Port $port already in use${NC}"
        return 1
    fi
    return 0
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    local main_file=$4

    echo -e "${BLUE}Starting $service_name on port $port...${NC}"

    # Check if port is available
    if ! check_port $port; then
        echo -e "${RED}✗ Cannot start $service_name - port $port in use${NC}"
        SERVICES_STATUS+=("$service_name:FAILED:Port in use")
        return 1
    fi

    cd $service_dir

    # Create venv if not exists
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        pip install -q --upgrade pip
        if [ -f "requirements.txt" ]; then
            pip install -q -r requirements.txt
        fi
        deactivate
    fi

    # Create logs directory
    mkdir -p logs

    # Start service
    source venv/bin/activate
    nohup python3 $main_file --port $port > logs/service.log 2>&1 &
    SERVICE_PID=$!
    echo $SERVICE_PID > service.pid
    deactivate

    cd - > /dev/null

    # Wait and check if service started
    sleep 2
    if ps -p $SERVICE_PID > /dev/null 2>&1; then
        echo -e "${GREEN}✓ $service_name started (PID: $SERVICE_PID)${NC}"
        SERVICES_STATUS+=("$service_name:RUNNING:$port:$SERVICE_PID")
        return 0
    else
        echo -e "${RED}✗ $service_name failed to start${NC}"
        SERVICES_STATUS+=("$service_name:FAILED:Start error")
        return 1
    fi
}

# Function to check service health
check_health() {
    local port=$1
    local max_attempts=5
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s -f http://localhost:$port/health > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
        ((attempt++))
    done
    return 1
}

echo "=========================================="
echo "PHASE 2: MVP Services"
echo "=========================================="
echo ""

# Medical Imaging AI (Port 5001)
start_service "Medical Imaging AI" \
    "medical-imaging-ai" \
    5001 \
    "src/main.py"

# AI Diagnostics (Port 5002)
start_service "AI Diagnostics" \
    "ai-diagnostics" \
    5002 \
    "src/main.py"

# Genomic Intelligence (Port 5007)
start_service "Genomic Intelligence" \
    "genomic-intelligence-service" \
    5007 \
    "src/main.py"

echo ""
echo "=========================================="
echo "PHASE 4: Additional Services"
echo "=========================================="
echo ""

# OBiCare (Port 5010)
start_service "OBiCare - Maternal Health" \
    "phase4-services/obicare" \
    5010 \
    "src/main.py"

# HIPAA Monitor (Port 5011)
start_service "HIPAA Compliance Monitor" \
    "phase4-services/hipaa-monitor" \
    5011 \
    "src/main.py"

echo ""
echo "=========================================="
echo "Performing Health Checks..."
echo "=========================================="
echo ""

sleep 3

for status in "${SERVICES_STATUS[@]}"; do
    IFS=':' read -r name state port pid <<< "$status"

    if [ "$state" == "RUNNING" ]; then
        if check_health $port; then
            echo -e "${GREEN}✓ $name: Healthy${NC}"
        else
            echo -e "${YELLOW}⚠️  $name: Started but not responding${NC}"
        fi
    else
        echo -e "${RED}✗ $name: $state${NC}"
    fi
done

echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo ""

echo "Services:"
for status in "${SERVICES_STATUS[@]}"; do
    IFS=':' read -r name state port pid <<< "$status"
    if [ "$state" == "RUNNING" ]; then
        echo "  ✓ $name - http://localhost:$port (PID: $pid)"
    else
        echo "  ✗ $name - $state"
    fi
done

echo ""
echo "API Documentation:"
echo "  - Medical Imaging AI:    http://localhost:5001/docs"
echo "  - AI Diagnostics:        http://localhost:5002/docs"
echo "  - Genomic Intelligence:  http://localhost:5007/docs"
echo "  - OBiCare:              http://localhost:5010/docs"
echo "  - HIPAA Monitor:        http://localhost:5011/docs"
echo ""

echo "To stop all services, run: ./stop_all_services.sh"
echo ""

# Count running services
running_count=$(echo "${SERVICES_STATUS[@]}" | grep -o "RUNNING" | wc -l)
total_count=${#SERVICES_STATUS[@]}

echo "Status: $running_count/$total_count services running"

if [ $running_count -eq $total_count ]; then
    echo -e "${GREEN}✓ All services deployed successfully!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  Some services failed to start${NC}"
    exit 1
fi
