# Auth Dashboard Frontend

Unified dashboard frontend for the BioMedical Intelligence Platform.

**Port:** 3000

## Features

- **Authentication**: Login, Register, MFA Setup
- **Patient Management**: List, search, view patients
- **Prediction History**: View AI predictions
- **User Management**: Admin user management (admin only)
- **Admin Panel**: Audit logs, system health (admin only)

## Quick Start

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local

# Run development server
npm run dev
```

Visit: http://localhost:3000

## Default Credentials

After creating a user via registration or using the backend API, you can login with your credentials.

## Project Structure

```
frontend/
├── app/                 # Next.js 14 app router
│   ├── login/
│   ├── register/
│   └── dashboard/
│       ├── patients/
│       ├── predictions/
│       ├── users/
│       └── admin/
├── components/          # React components
│   ├── auth/
│   └── dashboard/
└── lib/                # Utilities
    ├── api.ts          # API client
    └── AuthContext.tsx # Auth context
```

## Technologies

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Axios
- QR Code React
