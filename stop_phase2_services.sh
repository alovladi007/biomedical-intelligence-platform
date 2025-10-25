#!/bin/bash

# Stop Phase 2 MVP Services

echo "=========================================="
echo "Stopping Phase 2 MVP Services"
echo "=========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Medical Imaging AI
if [ -f "medical-imaging-ai/medical-imaging.pid" ]; then
    PID=$(cat medical-imaging-ai/medical-imaging.pid)
    kill $PID 2>/dev/null && echo -e "${GREEN}✓ Medical Imaging AI stopped (PID: $PID)${NC}" || echo -e "${RED}✗ Medical Imaging AI not running${NC}"
    rm medical-imaging-ai/medical-imaging.pid
fi

# AI Diagnostics
if [ -f "ai-diagnostics/ai-diagnostics.pid" ]; then
    PID=$(cat ai-diagnostics/ai-diagnostics.pid)
    kill $PID 2>/dev/null && echo -e "${GREEN}✓ AI Diagnostics stopped (PID: $PID)${NC}" || echo -e "${RED}✗ AI Diagnostics not running${NC}"
    rm ai-diagnostics/ai-diagnostics.pid
fi

# Genomic Intelligence
if [ -f "genomic-intelligence-service/genomic-intelligence.pid" ]; then
    PID=$(cat genomic-intelligence-service/genomic-intelligence.pid)
    kill $PID 2>/dev/null && echo -e "${GREEN}✓ Genomic Intelligence stopped (PID: $PID)${NC}" || echo -e "${RED}✗ Genomic Intelligence not running${NC}"
    rm genomic-intelligence-service/genomic-intelligence.pid
fi

echo ""
echo "All Phase 2 services stopped"
