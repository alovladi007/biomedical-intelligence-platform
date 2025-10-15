#!/bin/bash

# Simple startup script - starts one frontend at a time
# This is easier to debug and manage

set -e

echo "🚀 Starting BioMedical Platform Services..."
echo ""

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "📁 Working directory: $BASE_DIR"
echo ""

# Start AI Diagnostics Frontend (simplest to test)
echo "=== Starting AI Diagnostics Frontend on port 3001 ==="
cd "$BASE_DIR/ai-diagnostics/frontend"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    cp .env.example .env.local 2>/dev/null || echo "NEXT_PUBLIC_API_URL=http://localhost:5001" > .env.local
fi

echo "Starting Next.js dev server..."
echo "This will take 30-60 seconds to compile..."
echo ""
npm run dev

# Note: This script runs the frontend in foreground so you can see the output
# Press Ctrl+C to stop when you're done testing
