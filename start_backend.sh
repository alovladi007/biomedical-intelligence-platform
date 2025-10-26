#!/bin/bash
cd /Users/vladimirantoine/biomedical-intelligence-platform/auth-dashboard-service/backend
source venv/bin/activate
DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform" PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8100 --reload
