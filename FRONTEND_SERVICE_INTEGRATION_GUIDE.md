# Frontend Service Integration Guide

This guide shows how to integrate the existing service frontends with the new auth-dashboard-service.

## Overview

Each existing service frontend needs to:
1. Add authentication pages (login/register)
2. Wrap the app with AuthProvider
3. Update API client to use port 8100 for auth
4. Add protected route guards

## Example Integration: Medical Imaging AI

### Step 1: Install Dependencies

```bash
cd medical-imaging-ai/frontend
npm install axios
```

### Step 2: Copy Auth Components

Copy these files from `auth-dashboard-service/frontend`:
- `lib/api.ts` → `medical-imaging-ai/frontend/lib/api.ts`
- `lib/AuthContext.tsx` → `medical-imaging-ai/frontend/lib/AuthContext.tsx`
- `components/auth/LoginForm.tsx` → `medical-imaging-ai/frontend/components/auth/LoginForm.tsx`

### Step 3: Update Root Layout

**File:** `medical-imaging-ai/frontend/app/layout.tsx`

```typescript
import { AuthProvider } from '@/lib/AuthContext';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          {children}
        </AuthProvider>
      </body>
    </html>
  );
}
```

### Step 4: Add Login Page

**File:** `medical-imaging-ai/frontend/app/login/page.tsx`

```typescript
import LoginForm from '@/components/auth/LoginForm';

export default function LoginPage() {
  return <LoginForm />;
}
```

### Step 5: Add Protected Route Guard

**File:** `medical-imaging-ai/frontend/components/ProtectedRoute.tsx`

```typescript
'use client';

import { useAuth } from '@/lib/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
}
```

### Step 6: Wrap Main Pages

**File:** `medical-imaging-ai/frontend/app/page.tsx`

```typescript
import ProtectedRoute from '@/components/ProtectedRoute';
import MedicalImagingUI from '@/components/MedicalImagingUI';

export default function Home() {
  return (
    <ProtectedRoute>
      <MedicalImagingUI />
    </ProtectedRoute>
  );
}
```

### Step 7: Update Environment Variables

**File:** `medical-imaging-ai/frontend/.env.local`

```bash
# Auth API (port 8100)
NEXT_PUBLIC_AUTH_API_URL=http://localhost:8100

# Medical Imaging API (port 5001)
NEXT_PUBLIC_IMAGING_API_URL=http://localhost:5001
```

### Step 8: Update API Client

**File:** `medical-imaging-ai/frontend/lib/imagingAPI.ts`

```typescript
import axios from 'axios';

const imagingAPI = axios.create({
  baseURL: process.env.NEXT_PUBLIC_IMAGING_API_URL || 'http://localhost:5001',
});

// Add token to requests
imagingAPI.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default imagingAPI;
```

## Apply to All Services

Repeat the above steps for each service:

1. **AI Diagnostics** (port 3002, backend port 5002)
2. **Genomic Intelligence** (port 3007, backend port 5007)
3. **OBiCare** (port 3010, backend port 5010)
4. **HIPAA Monitor** (port 3011, backend port 5011)

## Quick Integration Checklist

For each service frontend:

- [ ] Install axios
- [ ] Copy auth components from auth-dashboard-service
- [ ] Wrap app with AuthProvider
- [ ] Add login page at `/login`
- [ ] Create ProtectedRoute component
- [ ] Wrap main pages with ProtectedRoute
- [ ] Update environment variables
- [ ] Update API client to include auth token
- [ ] Test login flow
- [ ] Test protected routes redirect to login
- [ ] Test API calls include auth token

## Testing

1. Start auth-dashboard-service backend (port 8100)
2. Start service backend (e.g., port 5001 for imaging)
3. Start service frontend (e.g., port 3001 for imaging)
4. Navigate to http://localhost:3001
5. Should redirect to /login
6. Login with valid credentials
7. Should redirect back to main page
8. API calls should work with auth token

## Shared Navigation

Optionally, add navigation to link between services:

```typescript
<nav>
  <Link href="http://localhost:3000/dashboard">Main Dashboard</Link>
  <Link href="http://localhost:3001">Medical Imaging</Link>
  <Link href="http://localhost:3002">AI Diagnostics</Link>
  {/* etc */}
</nav>
```

## Common Issues

### CORS Errors
- Ensure backend includes frontend port in CORS origins
- Backend CORS should include: `http://localhost:3001`, etc.

### Token Not Sent
- Check localStorage has `access_token`
- Verify interceptor is adding Authorization header
- Check browser console for errors

### Infinite Redirect Loop
- Ensure AuthProvider is checking token correctly
- Verify useEffect dependencies in ProtectedRoute
- Check router.push is not causing loop

## Session 4 Complete

Once all services are integrated:
- ✅ All frontends share same authentication
- ✅ All use JWT tokens from port 8100
- ✅ All redirect to login when unauthenticated
- ✅ All can access patient data from central database
- ✅ All API calls include auth token

