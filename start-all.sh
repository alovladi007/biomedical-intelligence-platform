#!/bin/bash

echo "🏥 BioMedical Intelligence Platform - Starting All Services"
echo "============================================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create logs directory
mkdir -p logs

# Services configuration: service_name:backend_port:frontend_port
SERVICES=(
  "ai-diagnostics:5001:3007"
  "medical-imaging:5002:3002"
  "biosensing:5003:3003"
  "hipaa-compliance:5004:3004"
  "biotensor-labs:5005:3005"
  "obicare:5006:3006"
  "genomic-intelligence:5007:3008"
  "drug-discovery-ai:5008:3009"
)

echo -e "${BLUE}🚀 Starting All Services...${NC}"
echo ""

# Function to start a service
start_service() {
  local service=$1
  local backend_port=$2
  local frontend_port=$3
  
  echo -e "${YELLOW}Starting ${service}...${NC}"
  
  # Start backend
  if [ -d "$service/backend" ]; then
    cd "$service/backend"
    PORT=$backend_port npm run dev > "../../logs/${service}-backend.log" 2>&1 &
    echo $! > "../../logs/${service}-backend.pid"
    cd ../..
    echo -e "  ${GREEN}✓${NC} Backend started on port $backend_port"
  fi
  
  # Start frontend
  if [ -d "$service/frontend" ]; then
    cd "$service/frontend"
    npm run dev > "../../logs/${service}-frontend.log" 2>&1 &
    echo $! > "../../logs/${service}-frontend.pid"
    cd ../..
    echo -e "  ${GREEN}✓${NC} Frontend started on port $frontend_port"
  fi
  
  echo ""
}

# Start all services
for service_info in "${SERVICES[@]}"; do
  IFS=':' read -r service backend_port frontend_port <<< "$service_info"
  start_service "$service" "$backend_port" "$frontend_port"
done

# Start simple HTTP server for main index.html if available
if [ -f "index.html" ]; then
  echo -e "${YELLOW}Starting main landing page...${NC}"
  python3 -m http.server 8080 > logs/landing.log 2>&1 &
  echo $! > logs/landing.pid
  echo -e "${GREEN}✓${NC} Landing page started on port 8080"
  echo ""
fi

echo ""
echo -e "${GREEN}✅ All services started successfully!${NC}"
echo ""
echo "🌐 Service URLs:"
echo "   Landing Page: http://localhost:8080"
echo "   AI Diagnostics: http://localhost:3007"
echo "   Medical Imaging: http://localhost:3002"
echo "   Biosensing: http://localhost:3003"
echo "   HIPAA Compliance: http://localhost:3004"
echo "   BioTensor Labs: http://localhost:3005"
echo "   OBiCare: http://localhost:3006"
echo "   Genomic Intelligence: http://localhost:3008"
echo "   Drug Discovery AI: http://localhost:3009"
echo ""
echo "📊 Backend APIs:"
echo "   AI Diagnostics API: http://localhost:5001"
echo "   Medical Imaging API: http://localhost:5002"
echo "   Biosensing API: http://localhost:5003"
echo "   HIPAA Compliance API: http://localhost:5004"
echo "   BioTensor Labs API: http://localhost:5005"
echo "   OBiCare API: http://localhost:5006"
echo "   Genomic Intelligence API: http://localhost:5007"
echo "   Drug Discovery AI API: http://localhost:5008"
echo ""
echo "📝 Logs are in ./logs directory"
echo "🛑 Run ./stop-all.sh to stop all services"
echo ""
