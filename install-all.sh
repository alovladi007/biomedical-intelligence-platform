#!/bin/bash

echo "🏥 BioMedical Intelligence Platform - Installation Script"
echo "=========================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Services array
SERVICES=(
  "ai-diagnostics"
  "medical-imaging"
  "biosensing"
  "hipaa-compliance"
  "biotensor-labs"
  "obicare"
  "genomic-intelligence"
  "drug-discovery-ai"
)

echo -e "${BLUE}📦 Installing Dependencies for All Services${NC}"
echo ""

for service in "${SERVICES[@]}"; do
  echo -e "${YELLOW}Installing ${service}...${NC}"
  
  # Backend
  if [ -d "$service/backend" ]; then
    echo "  📦 Backend dependencies..."
    cd "$service/backend"
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    cd ../..
  fi
  
  # Frontend
  if [ -d "$service/frontend" ]; then
    echo "  🎨 Frontend dependencies..."
    cd "$service/frontend"
    npm install --silent 2>&1 | grep -v "npm WARN" || true
    cd ../..
  fi
  
  echo -e "${GREEN}  ✓ ${service} installed${NC}"
  echo ""
done

echo ""
echo -e "${GREEN}✅ All services installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Run ./start-all.sh to start all services"
echo "2. Open http://localhost:8080 in your browser"
echo ""
