#!/bin/bash

# Biomedical Intelligence Platform - Service Shutdown Script
# This script stops both the backend and frontend services

echo "🛑 Stopping Biomedical Intelligence Platform services..."
echo ""

# Stop Backend
echo "Stopping Backend (port 8100)..."
BACKEND_PIDS=$(lsof -ti:8100)
if [ -n "$BACKEND_PIDS" ]; then
    echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
    echo "✅ Backend stopped"
else
    echo "ℹ️  Backend was not running"
fi

# Stop Frontend
echo "Stopping Frontend (port 8081)..."
FRONTEND_PIDS=$(lsof -ti:8081)
if [ -n "$FRONTEND_PIDS" ]; then
    echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
    echo "✅ Frontend stopped"
else
    echo "ℹ️  Frontend was not running"
fi

echo ""
echo "✅ All services stopped"
echo ""
echo "To restart: ./start-services.sh"
