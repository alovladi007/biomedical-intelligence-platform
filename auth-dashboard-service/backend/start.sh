#!/bin/bash

# Auth Dashboard Service Startup Script

echo "🚀 Starting Auth Dashboard Service..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "❌ Dependencies not installed!"
    echo "Please run: pip install -r requirements.txt"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found, copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your configuration"
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if PostgreSQL is accessible
echo "🔍 Checking database connection..."
if ! python -c "import psycopg2; conn = psycopg2.connect('$DATABASE_URL'); conn.close()" 2>/dev/null; then
    echo "❌ Cannot connect to database!"
    echo "Please make sure PostgreSQL is running and DATABASE_URL is correct"
    exit 1
fi

echo "✅ Database connection successful"
echo ""

# Start the service
echo "🎉 Starting Auth Dashboard Service on port 8100..."
echo "📚 API Documentation: http://localhost:8100/docs"
echo "📖 ReDoc: http://localhost:8100/redoc"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python app/main.py
