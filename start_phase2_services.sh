#!/bin/bash

# Start Phase 2 MVP Services
# Medical Imaging AI, AI Diagnostics, Genomic Intelligence

echo "=========================================="
echo "Starting Phase 2 MVP Services"
echo "=========================================="

# Colors for output
GREEN='\033[0.32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if virtual environments exist, create if not
echo -e "${BLUE}Checking Python environments...${NC}"

# Medical Imaging AI
if [ ! -d "medical-imaging-ai/venv" ]; then
    echo "Creating virtual environment for Medical Imaging AI..."
    cd medical-imaging-ai
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    cd ..
fi

# AI Diagnostics
if [ ! -d "ai-diagnostics/venv" ]; then
    echo "Creating virtual environment for AI Diagnostics..."
    cd ai-diagnostics
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    cd ..
fi

# Genomic Intelligence
if [ ! -d "genomic-intelligence-service/venv" ]; then
    echo "Creating virtual environment for Genomic Intelligence..."
    cd genomic-intelligence-service
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    deactivate
    cd ..
fi

echo -e "${GREEN}Virtual environments ready${NC}"
echo ""

# Start services
echo -e "${BLUE}Starting services...${NC}"

# Medical Imaging AI (Port 5001)
echo "Starting Medical Imaging AI on port 5001..."
cd medical-imaging-ai
source venv/bin/activate
nohup python3 src/main.py --port 5001 > logs/medical-imaging.log 2>&1 &
MEDICAL_PID=$!
echo $MEDICAL_PID > medical-imaging.pid
deactivate
cd ..
echo -e "${GREEN}✓ Medical Imaging AI started (PID: $MEDICAL_PID)${NC}"

# AI Diagnostics (Port 5002)
echo "Starting AI Diagnostics on port 5002..."
cd ai-diagnostics
source venv/bin/activate
nohup python3 src/main.py --port 5002 > logs/ai-diagnostics.log 2>&1 &
DIAGNOSTICS_PID=$!
echo $DIAGNOSTICS_PID > ai-diagnostics.pid
deactivate
cd ..
echo -e "${GREEN}✓ AI Diagnostics started (PID: $DIAGNOSTICS_PID)${NC}"

# Genomic Intelligence (Port 5007)
echo "Starting Genomic Intelligence on port 5007..."
cd genomic-intelligence-service
source venv/bin/activate
nohup python3 src/main.py --port 5007 > logs/genomic-intelligence.log 2>&1 &
GENOMIC_PID=$!
echo $GENOMIC_PID > genomic-intelligence.pid
deactivate
cd ..
echo -e "${GREEN}✓ Genomic Intelligence started (PID: $GENOMIC_PID)${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}All Phase 2 services started!${NC}"
echo "=========================================="
echo ""
echo "Services:"
echo "  - Medical Imaging AI:    http://localhost:5001"
echo "  - AI Diagnostics:        http://localhost:5002"
echo "  - Genomic Intelligence:  http://localhost:5007"
echo ""
echo "API Documentation:"
echo "  - http://localhost:5001/docs"
echo "  - http://localhost:5002/docs"
echo "  - http://localhost:5007/docs"
echo ""
echo "To stop services, run: ./stop_phase2_services.sh"
echo "To view logs:"
echo "  - tail -f medical-imaging-ai/logs/medical-imaging.log"
echo "  - tail -f ai-diagnostics/logs/ai-diagnostics.log"
echo "  - tail -f genomic-intelligence-service/logs/genomic-intelligence.log"
echo ""

# Health checks
sleep 3
echo "Performing health checks..."

curl -s http://localhost:5001/health > /dev/null && echo -e "${GREEN}✓ Medical Imaging AI: healthy${NC}" || echo -e "${RED}✗ Medical Imaging AI: unhealthy${NC}"
curl -s http://localhost:5002/health > /dev/null && echo -e "${GREEN}✓ AI Diagnostics: healthy${NC}" || echo -e "${RED}✗ AI Diagnostics: unhealthy${NC}"
curl -s http://localhost:5007/health > /dev/null && echo -e "${GREEN}✓ Genomic Intelligence: healthy${NC}" || echo -e "${RED}✗ Genomic Intelligence: unhealthy${NC}"

echo ""
