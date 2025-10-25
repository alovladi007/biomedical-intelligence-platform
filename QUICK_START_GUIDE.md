# Quick Start Guide - Complete Platform

This guide will help you start the complete BioMedical Intelligence Platform with all components.

## 🎯 Prerequisites Check

Before starting, ensure you have:

- [x] Python 3.9+
- [x] Node.js 18+
- [x] PostgreSQL 15
- [x] Docker & Docker Compose
- [x] Git

## 🚀 Option 1: Full Stack Startup (Recommended)

### Step 1: Start Infrastructure Services

```bash
# Start PostgreSQL, Prometheus, Grafana, Redis, Elasticsearch, Kibana
cd infrastructure
docker-compose up -d

# Verify services are running
docker-compose ps

# Expected output:
# - postgresql (port 5432) - Up
# - prometheus (port 9090) - Up
# - grafana (port 3000) - Up
# - redis (port 6379) - Up
# - elasticsearch (port 9200) - Up
# - kibana (port 5601) - Up
```

### Step 2: Initialize Database

```bash
# Set database URL
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/biomedical_platform"

# Run migrations
cd database
alembic -c config/alembic.ini upgrade head

# Verify database is ready
psql $DATABASE_URL -c "SELECT tablename FROM pg_tables WHERE schemaname='public';"
```

### Step 3: Start Backend Service (Terminal 1)

```bash
# Navigate to backend
cd ../../../auth-dashboard-service/backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Copy environment file (first time only)
cp .env.example .env

# Edit .env if needed (optional)
# nano .env

# Start backend
./start.sh

# Or manually:
python app/main.py

# Expected output:
# ✅ Database initialized
# ✅ RBAC permissions initialized
# ✅ Database health check passed
# 🎉 Auth Dashboard Service started successfully on port 8100
# INFO: Uvicorn running on http://0.0.0.0:8100
```

### Step 4: Start Frontend (Terminal 2)

```bash
# Navigate to frontend
cd auth-dashboard-service/frontend

# Install dependencies (first time only)
npm install

# Copy environment file (first time only)
cp .env.local.example .env.local

# Start development server
npm run dev

# Expected output:
# ▲ Next.js 14.2.0
# - Local:        http://localhost:3000
# - Network:      http://192.168.x.x:3000
# ✓ Ready in 2.5s
```

### Step 5: Verify Everything is Running

Open your browser and check:

1. **Frontend Dashboard**: http://localhost:3000
   - Should redirect to login page

2. **Backend API Docs**: http://localhost:8100/docs
   - Should show Swagger UI with all endpoints

3. **Backend Health**: http://localhost:8100/health
   - Should return: `{"status": "healthy", "database": "connected"}`

4. **Grafana**: http://localhost:3000 (infrastructure)
   - Login: admin/admin

5. **Prometheus**: http://localhost:9090
   - Should show Prometheus UI

---

## 🧪 Option 2: Test the System

### Create Your First User

**Option A: Via Frontend (Recommended)**

1. Open http://localhost:3000
2. Click "Sign up"
3. Fill in the form:
   - First Name: John
   - Last Name: Doe
   - Username: johndoe
   - Email: john@example.com
   - Password: SecurePass123!
   - Confirm Password: SecurePass123!
   - Role: Physician
4. Click "Create Account"
5. Login with your credentials

**Option B: Via API**

```bash
# Create user via API
curl -X POST http://localhost:8100/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890",
    "role": "physician"
  }'

# Expected response:
# {
#   "user_id": 1,
#   "username": "johndoe",
#   "email": "john@example.com",
#   "role": "physician",
#   "message": "User registered successfully"
# }
```

### Login and Get Token

```bash
# Login
curl -X POST http://localhost:8100/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "SecurePass123!"
  }'

# Save the access_token from response
export TOKEN="<your_access_token_here>"
```

### Create a Patient

```bash
# Create patient
curl -X POST http://localhost:8100/api/patients \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "mrn": "MRN001",
    "first_name": "Jane",
    "last_name": "Smith",
    "date_of_birth": "1990-01-15",
    "sex": "female",
    "email": "jane.smith@example.com",
    "phone": "+1234567890"
  }'

# Expected response:
# {
#   "id": 1,
#   "mrn": "MRN001",
#   "first_name": "Jane",
#   "last_name": "Smith",
#   ...
# }
```

### View Patients in Frontend

1. Login to http://localhost:3000
2. Navigate to "Patients" from sidebar
3. You should see your created patient

---

## 🔧 Troubleshooting

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Check what's using the port
lsof -i :8100  # Backend
lsof -i :3000  # Frontend

# Kill the process
kill -9 <PID>

# Or use a different port
PORT=8101 python app/main.py  # Backend
npm run dev -- -p 3001         # Frontend
```

### Issue: Database Connection Failed

**Error:** `Cannot connect to database`

**Solution:**
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Restart PostgreSQL
cd infrastructure
docker-compose restart postgresql

# Verify connection
psql postgresql://postgres:postgres@localhost:5432/biomedical_platform -c "SELECT 1;"

# Check DATABASE_URL in .env
cat auth-dashboard-service/backend/.env | grep DATABASE_URL
```

### Issue: Module Not Found (Backend)

**Error:** `ModuleNotFoundError: No module named 'fastapi'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### Issue: Module Not Found (Frontend)

**Error:** `Cannot find module 'next'`

**Solution:**
```bash
# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall dependencies
npm install

# Clear cache
npm cache clean --force
npm install
```

### Issue: CORS Error

**Error:** `Access to XMLHttpRequest blocked by CORS policy`

**Solution:**
1. Check backend CORS configuration in `app/main.py`
2. Ensure frontend URL is in allowed origins
3. Restart backend after changes

### Issue: Token Expired

**Error:** `401 Unauthorized`

**Solution:**
- Login again to get new token
- Frontend should automatically refresh token
- Check browser console for errors

---

## 📊 Monitoring

### Check Backend Metrics

```bash
# Prometheus metrics
curl http://localhost:8100/metrics

# Health check
curl http://localhost:8100/health
```

### View Grafana Dashboards

1. Open http://localhost:3000 (Grafana)
2. Login: admin/admin
3. Go to Dashboards
4. View pre-configured dashboards

### View Audit Logs

**Via Frontend:**
1. Login as admin
2. Navigate to Admin Panel
3. View Recent Audit Logs

**Via API:**
```bash
curl -X GET "http://localhost:8100/api/admin/audit-logs?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🎯 Testing Checklist

Use this checklist to verify everything works:

### Backend Tests
- [ ] Backend starts without errors
- [ ] Database connection successful
- [ ] API docs accessible at /docs
- [ ] Health check returns healthy
- [ ] Can create user via /auth/register
- [ ] Can login via /auth/login
- [ ] Can access /auth/me with token
- [ ] Can create patient
- [ ] Can list patients
- [ ] Can view predictions
- [ ] Admin can access audit logs

### Frontend Tests
- [ ] Frontend loads at localhost:3000
- [ ] Registration page works
- [ ] Login page works
- [ ] Redirects to dashboard after login
- [ ] Dashboard shows navigation
- [ ] Patients page loads
- [ ] Predictions page loads
- [ ] Admin panel loads (for admin users)
- [ ] Logout works
- [ ] Token refresh works

### Integration Tests
- [ ] Frontend calls backend API successfully
- [ ] Token is sent in headers
- [ ] Protected routes redirect to login
- [ ] CORS works correctly
- [ ] Error messages display properly

---

## 🚀 Production Deployment

For production deployment, see:
- `DEPLOYMENT_GUIDE.md` - Infrastructure deployment
- `auth-dashboard-service/backend/README.md` - Backend deployment
- `auth-dashboard-service/frontend/README.md` - Frontend deployment

---

## 📚 Additional Resources

- **Backend API Docs**: http://localhost:8100/docs
- **Backend README**: `auth-dashboard-service/backend/README.md`
- **Frontend README**: `auth-dashboard-service/frontend/README.md`
- **Integration Guide**: `FRONTEND_SERVICE_INTEGRATION_GUIDE.md`
- **Complete Summary**: `SESSIONS_COMPLETE_SUMMARY.md`

---

## 💡 Tips

1. **Keep multiple terminals open:**
   - Terminal 1: Backend
   - Terminal 2: Frontend
   - Terminal 3: Testing/CLI commands

2. **Use browser DevTools:**
   - Network tab to see API calls
   - Console tab to see errors
   - Application tab to view localStorage (tokens)

3. **Monitor logs:**
   - Backend: Check terminal for errors
   - Frontend: Check browser console
   - Database: Check Docker logs

4. **Backup your data:**
   - Regular database backups
   - Export audit logs
   - Save environment files

---

## 🎉 Next Steps

Once everything is running:

1. **Create more users** with different roles
2. **Add more patients** to test patient management
3. **Explore the admin panel** (if you have admin role)
4. **Set up MFA** for enhanced security
5. **Integrate other services** using the integration guide
6. **Customize the dashboard** to your needs

---

**Need Help?**

If you encounter issues not covered here:
1. Check the error message carefully
2. Look in the respective README files
3. Check the GitHub issues
4. Review the API documentation

**Happy coding!** 🚀
