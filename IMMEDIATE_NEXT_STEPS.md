# Immediate Next Steps - Get Backend Running

## Current Status

✅ **Frontend is RUNNING** - http://localhost:8081
❌ **Backend is NOT running** - Needs database

## Why Backend Won't Start

The backend requires:
1. PostgreSQL database running
2. Database initialized with tables
3. Then the backend can start

## Option 1: Start with Docker (Recommended)

### Step 1: Start Docker Desktop
1. Open Docker Desktop application on your Mac
2. Wait for it to fully start (you'll see the whale icon in menu bar)

### Step 2: Start PostgreSQL
```bash
cd /Users/vladimirantoine/biomedical-intelligence-platform/infrastructure
docker-compose up -d postgres

# Wait 10 seconds for PostgreSQL to initialize
sleep 10

# Verify it's running
docker-compose ps
```

### Step 3: Initialize Database
```bash
# Set database URL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"

# Run migrations
cd database
alembic -c config/alembic.ini upgrade head
```

### Step 4: Start Backend
```bash
cd ../../auth-dashboard-service/backend
source venv/bin/activate
PYTHONPATH=. python -m app.main
```

### Step 5: Create Your First User
Once backend is running, open a new terminal:

```bash
curl -X POST http://localhost:8100/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "AdminPass123!",
    "first_name": "Admin",
    "last_name": "User",
    "role": "admin"
  }'
```

### Step 6: Login
1. Go to http://localhost:8081
2. Username: `admin`
3. Password: `AdminPass123!`

---

## Option 2: Without Docker (If Docker Issues Persist)

If Docker won't start, you can install PostgreSQL directly:

### Install PostgreSQL (Mac)
```bash
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb biomedical_platform

# Set database URL
export DATABASE_URL="postgresql://localhost:5432/biomedical_platform"

# Then continue with Step 3 above
```

---

## Option 3: Quick Test Without Database (SQLite)

If you just want to see the frontend and test quickly, we can create a demo mode:

1. Visit http://localhost:8081
2. The login page is there
3. Registration form is there
4. But without backend, authentication won't work

**You'll need the backend for actual login to work!**

---

## Troubleshooting

### Docker Won't Start
- Make sure Docker Desktop is installed
- Try restarting Docker Desktop
- Check Activity Monitor - kill any stuck Docker processes
- Restart your computer if needed

### Backend Errors
**Error:** `ModuleNotFoundError`
**Fix:** Make sure you're in the correct directory and venv is activated

**Error:** `Database connection failed`
**Fix:** Make sure PostgreSQL is running and DATABASE_URL is correct

**Error:** `Port 8100 already in use`
**Fix:** Kill the process: `lsof -ti:8100 | xargs kill -9`

### Frontend Issues
**Error:** `ECONNREFUSED`
**Fix:** This means backend isn't running - follow steps above

**Can't see login page**
**Fix:** Make sure you're going to http://localhost:8081 (not 8080)

---

## Current Services Status

Run this to check what's running:

```bash
# Check frontend
lsof -i :8081 | grep LISTEN

# Check backend
lsof -i :8100 | grep LISTEN

# Check PostgreSQL
lsof -i :5432 | grep LISTEN

# Check Docker
docker ps
```

---

## What Works Now

✅ Frontend UI - http://localhost:8081
✅ Login page visible
✅ Register page visible
✅ Dashboard layout exists

## What Needs Backend

❌ Actually logging in
❌ Creating users
❌ Viewing patients
❌ Viewing predictions
❌ All data operations

---

## Quick Command Reference

```bash
# Start everything
cd infrastructure && docker-compose up -d postgres
cd ../auth-dashboard-service/backend
source venv/bin/activate && PYTHONPATH=. python -m app.main

# Stop everything
# Ctrl+C in backend terminal
docker-compose down

# Check logs
tail -f /tmp/backend.log
tail -f /tmp/frontend.log

# Restart frontend (if needed)
cd auth-dashboard-service/frontend
npm run dev
```

---

## Summary

**To get login working:**
1. Start Docker Desktop ⚠️ (REQUIRED)
2. Start PostgreSQL (via Docker)
3. Initialize database (run migrations)
4. Start backend
5. Create first user
6. Login at http://localhost:8081

**Current blockers:**
- Docker not running OR
- PostgreSQL not started OR
- Database not initialized

Once you complete the above steps, you'll be able to:
- ✅ Login/Register
- ✅ Manage patients
- ✅ View predictions
- ✅ Use admin panel

---

Need help? Check:
- Backend logs: `/tmp/backend.log`
- Frontend logs: `/tmp/frontend.log`
- Docker logs: `docker-compose logs postgres`
