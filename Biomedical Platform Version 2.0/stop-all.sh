#!/bin/bash

echo "🛑 BioMedical Intelligence Platform - Stopping All Services"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Stop services by PID files
if [ -d "logs" ]; then
  for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
      pid=$(cat "$pidfile")
      service_name=$(basename "$pidfile" .pid)
      
      if kill -0 "$pid" 2>/dev/null; then
        kill "$pid" 2>/dev/null
        echo -e "${GREEN}✓${NC} Stopped $service_name (PID: $pid)"
      fi
      
      rm "$pidfile"
    fi
  done
fi

# Kill any remaining processes on our ports
echo ""
echo "Cleaning up ports..."
for port in 5001 5002 5003 5004 5005 5006 3007 3002 3003 3004 3005 3006 8080; do
  pid=$(lsof -ti:$port 2>/dev/null)
  if [ ! -z "$pid" ]; then
    kill -9 $pid 2>/dev/null
    echo -e "${GREEN}✓${NC} Cleaned port $port"
  fi
done

echo ""
echo -e "${GREEN}✅ All services stopped successfully!${NC}"
echo ""
