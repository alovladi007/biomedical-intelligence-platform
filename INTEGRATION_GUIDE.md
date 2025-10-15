# Frontend-Backend Integration Guide

**Biomedical Intelligence Platform**
**Last Updated**: October 15, 2025

---

## 🎯 Overview

This guide walks you through connecting the frontend services to their corresponding backend APIs. All frontends are currently running with mock data. Follow these steps to integrate them with real backend services.

---

## 📋 Current Status

### ✅ Ready to Integrate

| Frontend | Port | Backend | API Port | Integration Status |
|----------|------|---------|----------|-------------------|
| Medical Imaging AI | 3002 | Python FastAPI | 5002 | ⏳ Backend needs start |
| Biosensing | 3003 | Node.js Express | 5003 | ⏳ Port conflict |
| HIPAA Compliance | 3004 | Node.js Express | 5004 | ✅ Backend running |
| BioTensor Labs | 3005 | Python FastAPI | 5005 | ⏳ Backend needs start |
| AI Diagnostics | 3006 | Node.js Express | 5001 | ✅ Backend running |
| MYNX NatalCare | 3006 | Node.js Express | 5006 | ⏳ Backend needs start |

---

## 🚀 Step-by-Step Integration

### Step 1: Start All Backend Services

First, ensure all backend services are running:

```bash
cd biomedical-platform
./START_ALL_BACKENDS.sh
```

Or start individually (see [PLATFORM_STATUS.md](PLATFORM_STATUS.md) for details).

### Step 2: Verify Backend Health

Check that all backends are responding:

```bash
# Quick health check
for port in 5001 5002 5003 5004 5005 5006; do
  echo "Port $port:"
  curl -s http://localhost:$port/health | jq .
done
```

Expected output for each:
```json
{
  "status": "healthy",
  "service": "service-name",
  "version": "1.0.0",
  "timestamp": "2025-10-15T..."
}
```

### Step 3: Configure Frontend Environment Variables

Each frontend needs to know its backend API URL. Update `.env.local` files:

#### AI Diagnostics Frontend

```bash
cd ai-diagnostics/frontend
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:5001
NEXT_PUBLIC_API_VERSION=v1
NEXT_PUBLIC_DEMO_MODE=false
EOF
```

#### Medical Imaging AI Frontend

```bash
cd medical-imaging-ai/frontend
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:5002
NEXT_PUBLIC_PACS_URL=http://localhost:8042
NEXT_PUBLIC_DEMO_MODE=false
EOF
```

#### Biosensing Frontend

```bash
cd biosensing/frontend
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:5003
NEXT_PUBLIC_WS_URL=ws://localhost:5003
NEXT_PUBLIC_DEMO_MODE=false
EOF
```

#### HIPAA Compliance Frontend

```bash
cd hipaa-compliance/frontend
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:5004
NEXT_PUBLIC_DEMO_MODE=false
EOF
```

#### BioTensor Labs Frontend

```bash
cd biotensor-labs/frontend
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:5005
NEXT_PUBLIC_MLFLOW_URL=http://localhost:5000
NEXT_PUBLIC_DEMO_MODE=false
EOF
```

#### MYNX NatalCare Frontend

```bash
cd mynx-natalcare/frontend
cat > .env.local <<EOF
NEXT_PUBLIC_API_URL=http://localhost:5006
NEXT_PUBLIC_DEMO_MODE=false
EOF
```

### Step 4: Update API Client Configuration

Each frontend has an API client. Update them to use environment variables:

#### Example: AI Diagnostics API Client

File: `ai-diagnostics/frontend/src/lib/api.ts`

```typescript
// Before (hardcoded)
const API_URL = 'http://localhost:5001';

// After (environment variable)
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5001';
```

Apply this pattern to all API clients:
- `medical-imaging-ai/frontend/src/lib/api.ts`
- `biosensing/frontend/src/lib/api.ts`
- `hipaa-compliance/frontend/src/lib/api.ts`
- `biotensor-labs/frontend/src/lib/api.ts`
- `mynx-natalcare/frontend/src/lib/api.ts`

### Step 5: Restart Frontend Services

After updating environment variables, restart frontends:

```bash
# Stop all frontends (Ctrl+C in each terminal)
# Or kill processes
pkill -f "next dev"

# Restart each frontend
cd ai-diagnostics/frontend && npm run dev &
cd medical-imaging-ai/frontend && npm run dev &
cd biosensing/frontend && npm run dev &
cd hipaa-compliance/frontend && npm run dev &
cd biotensor-labs/frontend && npm run dev &
cd mynx-natalcare/frontend && npm run dev &
```

### Step 6: Test Integration

Visit each frontend and test API connectivity:

#### AI Diagnostics (Port 3006)
```bash
# Open in browser
open http://localhost:3006

# Test API call from browser console:
fetch('http://localhost:5001/api/v1/diagnostics')
  .then(r => r.json())
  .then(console.log)
```

#### Medical Imaging AI (Port 3002)
```bash
open http://localhost:3002

# Test API
fetch('http://localhost:5002/health')
  .then(r => r.json())
  .then(console.log)
```

Repeat for all services.

---

## 🔧 Common Integration Issues

### Issue 1: CORS Errors

**Symptom**: Browser console shows CORS errors

**Solution**: Ensure backend CORS is configured:

```typescript
// Backend: src/index.ts
app.use(cors({
  origin: [
    'http://localhost:3000',
    'http://localhost:3001',
    'http://localhost:3002',
    'http://localhost:3003',
    'http://localhost:3004',
    'http://localhost:3005',
    'http://localhost:3006'
  ],
  credentials: true
}));
```

### Issue 2: Connection Refused

**Symptom**: `ERR_CONNECTION_REFUSED`

**Solution**: Backend is not running. Start it:

```bash
cd <service>/backend
npm run dev  # For Node.js
# OR
source venv/bin/activate && uvicorn app.main:app --reload  # For Python
```

### Issue 3: 404 Not Found

**Symptom**: API endpoints return 404

**Solution**: Check endpoint paths match between frontend and backend:

```typescript
// Frontend
const response = await fetch(`${API_URL}/api/v1/diagnostics`);

// Backend should have:
app.get('/api/v1/diagnostics', handler);
```

### Issue 4: Environment Variables Not Loaded

**Symptom**: Frontend still uses hardcoded URLs

**Solution**:
1. Restart Next.js dev server (it caches .env)
2. Ensure `.env.local` exists and has correct values
3. Check for typos in variable names (must start with `NEXT_PUBLIC_`)

---

## 📊 API Endpoint Reference

### AI Diagnostics (Port 5001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/diagnostics` | Create diagnostic analysis |
| GET | `/api/v1/diagnostics/:id` | Get diagnostic result |
| POST | `/api/v1/risk-assessment` | Calculate risk scores |
| POST | `/api/v1/drug-discovery` | Drug molecule generation |

### Medical Imaging AI (Port 5002)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/upload` | Upload DICOM image |
| POST | `/api/v1/analyze` | Analyze image |
| GET | `/api/v1/gradcam/:imageId` | Get Grad-CAM heatmap |
| POST | `/api/v1/triage` | Automatic triage |
| GET | `/api/v1/worklist` | Get worklist |

### Biosensing (Port 5003)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/devices/register` | Register IoT device |
| POST | `/api/v1/devices/:id/readings` | Submit sensor reading |
| GET | `/api/v1/devices/:id/status` | Get device status |
| GET | `/api/v1/patients/:id/alerts` | Get patient alerts |
| WS | `/` | WebSocket connection |

### HIPAA Compliance (Port 5004)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/encrypt` | Encrypt PHI data |
| POST | `/api/v1/decrypt` | Decrypt PHI data |
| GET | `/api/v1/audit-logs` | Get audit logs |
| POST | `/api/v1/baa/create` | Create BAA |
| GET | `/api/v1/compliance/report` | Compliance report |

### BioTensor Labs (Port 5005)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/experiments` | Create experiment |
| GET | `/api/v1/experiments/:id` | Get experiment details |
| POST | `/api/v1/models/deploy` | Deploy model |
| POST | `/api/v1/signal-processing` | Process biosignal |
| GET | `/api/v1/metrics/:experimentId` | Get experiment metrics |

### MYNX NatalCare (Port 5006)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/pregnancy` | Create pregnancy record |
| POST | `/api/v1/prenatal-visit` | Record prenatal visit |
| POST | `/api/v1/risk-assessment` | Calculate pregnancy risk |
| GET | `/api/v1/monitoring/:id` | Get real-time monitoring |
| POST | `/api/v1/alerts/acknowledge` | Acknowledge alert |

---

## 🧪 Testing Integration

### Manual Testing Checklist

For each service:

- [ ] Backend health check responds
- [ ] Frontend loads without errors
- [ ] API calls succeed (check Network tab)
- [ ] Data displays correctly
- [ ] Error handling works (test invalid input)
- [ ] Loading states show during API calls

### Automated Testing

Create integration tests:

```typescript
// Example: ai-diagnostics/frontend/__tests__/integration/api.test.ts
describe('AI Diagnostics API Integration', () => {
  it('should fetch diagnostic results', async () => {
    const response = await fetch('http://localhost:5001/api/v1/diagnostics');
    expect(response.status).toBe(200);
    const data = await response.json();
    expect(data).toHaveProperty('results');
  });
});
```

Run tests:
```bash
npm test
```

---

## 🔐 Authentication Integration

### Step 1: Implement JWT Authentication

Backend:
```typescript
// shared/middleware/auth.ts
export const authenticateJWT = (req, res, next) => {
  const token = req.headers.authorization?.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Unauthorized' });

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(403).json({ error: 'Invalid token' });
  }
};
```

### Step 2: Frontend Auth Client

```typescript
// shared-frontend/lib/auth.ts
export class AuthClient {
  private token: string | null = null;

  async login(email: string, password: string) {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const { token } = await response.json();
    this.token = token;
    localStorage.setItem('token', token);
  }

  getAuthHeaders() {
    return {
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    };
  }
}
```

### Step 3: Protected API Calls

```typescript
// Frontend API client
const authClient = new AuthClient();

async function fetchProtectedData() {
  const response = await fetch(`${API_URL}/api/v1/diagnostics`, {
    headers: authClient.getAuthHeaders()
  });
  return response.json();
}
```

---

## 📚 Next Steps After Integration

1. **Add Error Boundaries**
   - Implement React Error Boundaries
   - Add global error handler

2. **Implement Loading States**
   - Add skeleton loaders
   - Show progress indicators

3. **Add Offline Support**
   - Service Workers
   - Cache API responses
   - Queue requests when offline

4. **Performance Optimization**
   - Implement request caching
   - Add request debouncing
   - Optimize bundle size

5. **Monitoring**
   - Add analytics
   - Log API errors
   - Track user actions

---

## 🐛 Debugging Tips

### View Backend Logs

```bash
# Node.js backends
cd <service>/backend
npm run dev  # Logs show in terminal

# Python backends
cd <service>/backend
source venv/bin/activate
uvicorn app.main:app --reload --log-level debug
```

### View Frontend Network Requests

1. Open browser DevTools (F12)
2. Go to Network tab
3. Filter by "XHR" or "Fetch"
4. Click on request to see details

### Test API Endpoints Directly

```bash
# Using curl
curl -X POST http://localhost:5001/api/v1/diagnostics \
  -H "Content-Type: application/json" \
  -d '{"patientId": "123", "data": {...}}'

# Using httpie
http POST http://localhost:5001/api/v1/diagnostics \
  patientId=123 data:='{...}'
```

---

## ✅ Integration Complete Checklist

- [ ] All backends running and healthy
- [ ] All frontends configured with backend URLs
- [ ] CORS configured on all backends
- [ ] API endpoints tested and working
- [ ] Authentication implemented
- [ ] Error handling in place
- [ ] Loading states added
- [ ] Integration tests passing
- [ ] Documentation updated

---

## 📞 Need Help?

- Check [PLATFORM_STATUS.md](PLATFORM_STATUS.md) for service status
- See [README.md](README.md) for architecture overview
- Review backend logs for errors
- Open GitHub issue for bugs

---

**Happy Integrating! 🚀**

© 2025 M.Y. Engineering and Technologies
