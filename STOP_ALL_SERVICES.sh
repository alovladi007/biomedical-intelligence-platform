#!/bin/bash

# Stop All Services Script

echo "=========================================="
echo "Stopping All Services"
echo "=========================================="

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Function to stop a service
stop_service() {
    local service_name=$1
    local service_dir=$2

    if [ -f "$service_dir/service.pid" ]; then
        PID=$(cat $service_dir/service.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID 2>/dev/null
            echo -e "${GREEN}✓ $service_name stopped (PID: $PID)${NC}"
        else
            echo -e "${RED}✗ $service_name not running${NC}"
        fi
        rm $service_dir/service.pid
    else
        echo "  $service_name: No PID file found"
    fi
}

# Stop Phase 2 services
stop_service "Medical Imaging AI" "medical-imaging-ai"
stop_service "AI Diagnostics" "ai-diagnostics"
stop_service "Genomic Intelligence" "genomic-intelligence-service"

# Stop Phase 4 services
stop_service "OBiCare" "phase4-services/obicare"
stop_service "HIPAA Monitor" "phase4-services/hipaa-monitor"

echo ""
echo "All services stopped"
