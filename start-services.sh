#!/bin/bash

# Biomedical Intelligence Platform - Service Startup Script
# This script starts both the backend and frontend services

echo "🚀 Starting Biomedical Intelligence Platform..."
echo ""

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running!"
    echo "   Please start Docker Desktop and ensure PostgreSQL container is running"
    echo "   Run: docker-compose up -d (in infrastructure directory)"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Start Backend
echo ""
echo "🔧 Starting Backend API (port 8100)..."
cd /Users/vladimirantoine/biomedical-intelligence-platform/auth-dashboard-service/backend
source venv/bin/activate
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"
export PYTHONPATH=.

# Kill any existing backend processes
lsof -ti:8100 | xargs kill -9 2>/dev/null

# Start backend in background
nohup uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

sleep 3

# Check if backend started successfully
if curl -s http://localhost:8100/health > /dev/null 2>&1; then
    echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    echo "   API: http://localhost:8100"
    echo "   Docs: http://localhost:8100/docs"
else
    echo "❌ Backend failed to start"
    echo "   Check logs: tail -f /tmp/backend.log"
    exit 1
fi

# Start Frontend
echo ""
echo "🎨 Starting Frontend Dashboard (port 8081)..."
cd /Users/vladimirantoine/biomedical-intelligence-platform/auth-dashboard-service/frontend

# Kill any existing frontend processes
lsof -ti:8081 | xargs kill -9 2>/dev/null

# Start frontend in background
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!

sleep 5

# Check if frontend started successfully
if curl -s http://localhost:8081 > /dev/null 2>&1; then
    echo "✅ Frontend started successfully (PID: $FRONTEND_PID)"
    echo "   Dashboard: http://localhost:8081"
else
    echo "⚠️  Frontend may still be starting..."
    echo "   Check logs: tail -f /tmp/frontend.log"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Services Started!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Frontend:  http://localhost:8081"
echo "🔧 Backend:   http://localhost:8100"
echo "📚 API Docs:  http://localhost:8100/docs"
echo ""
echo "👤 Login Credentials:"
echo "   Username: admin"
echo "   Password: SecurePass123!"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f /tmp/backend.log"
echo "   Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop services:"
echo "   ./stop-services.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
