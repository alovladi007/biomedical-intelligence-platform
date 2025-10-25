# 🚀 Quick Start Guide

## Prerequisites
- Node.js >= 18.0.0
- npm >= 9.0.0

## Installation (2 minutes)

```bash
# 1. Make scripts executable
chmod +x *.sh

# 2. Install all dependencies
./install-all.sh

# This will install dependencies for all 6 services
# Estimated time: 2-3 minutes
```

## Starting the Platform (30 seconds)

```bash
# Start all services at once
./start-all.sh

# This starts:
# - 6 backend APIs (ports 5001-5006)
# - 6 frontend apps (ports 3007, 3002-3006)
# - Landing page (port 8080)
```

## Access the Platform

### Main Landing Page
**http://localhost:8080**

This is your starting point with links to all services.

### Individual Services

| Service | Frontend | Backend API |
|---------|----------|-------------|
| **AI Diagnostics** | http://localhost:3007 | http://localhost:5001 |
| **Medical Imaging** | http://localhost:3002 | http://localhost:5002 |
| **Biosensing** | http://localhost:3003 | http://localhost:5003 |
| **HIPAA Compliance** | http://localhost:3004 | http://localhost:5004 |
| **BioTensor Labs** | http://localhost:3005 | http://localhost:5005 |
| **MYNX NatalCare** | http://localhost:3006 | http://localhost:5006 |

## Testing the APIs

```bash
# Check all backend health endpoints
curl http://localhost:5001/health  # AI Diagnostics
curl http://localhost:5002/health  # Medical Imaging
curl http://localhost:5003/health  # Biosensing
curl http://localhost:5004/health  # HIPAA Compliance
curl http://localhost:5005/health  # BioTensor Labs
curl http://localhost:5006/health  # MYNX NatalCare
```

## Stopping the Platform

```bash
# Stop all services
./stop-all.sh
```

## Docker Deployment

```bash
# Build and start with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all containers
docker-compose down
```

## Project Structure

```
biomedical-platform/
├── ai-diagnostics/          # AI Diagnostics Service
│   ├── backend/             # Express API (Port 5001)
│   └── frontend/            # Next.js App (Port 3007)
├── medical-imaging/         # Medical Imaging Service
│   ├── backend/             # Express API (Port 5002)
│   └── frontend/            # Next.js App (Port 3002)
├── biosensing/              # Biosensing Service
│   ├── backend/             # Express API (Port 5003)
│   └── frontend/            # Next.js App (Port 3003)
├── hipaa-compliance/        # HIPAA Compliance Service
│   ├── backend/             # Express API (Port 5004)
│   └── frontend/            # Next.js App (Port 3004)
├── biotensor-labs/          # BioTensor Labs Service
│   ├── backend/             # Express API (Port 5005)
│   └── frontend/            # Next.js App (Port 3005)
├── mynx-natalcare/          # MYNX NatalCare Service
│   ├── backend/             # Express API (Port 5006)
│   └── frontend/            # Next.js App (Port 3006)
├── index.html               # Main landing page
├── install-all.sh          # Installation script
├── start-all.sh            # Startup script
├── stop-all.sh             # Shutdown script
├── docker-compose.yml       # Docker deployment
└── README.md                # Full documentation
```

## Development Mode

Run services individually for development:

```bash
# Backend with hot reload
cd ai-diagnostics/backend
npm run dev

# Frontend with hot reload
cd ai-diagnostics/frontend  
npm run dev
```

## Production Build

```bash
# Build all services
for service in ai-diagnostics medical-imaging biosensing hipaa-compliance biotensor-labs mynx-natalcare; do
  cd $service/backend && npm run build && cd ../..
  cd $service/frontend && npm run build && cd ../..
done
```

## Troubleshooting

### Port Already in Use
```bash
# Stop all services first
./stop-all.sh

# Or manually kill processes
lsof -ti:5001 | xargs kill -9  # Repeat for other ports
```

### Dependencies Not Installing
```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
find . -name "node_modules" -type d -exec rm -rf {} +
./install-all.sh
```

### Services Not Starting
```bash
# Check logs
tail -f logs/*.log

# Verify Node.js version
node --version  # Should be >= 18.0.0
```

## Next Steps

1. **Explore the Services**: Visit each frontend application
2. **Test the APIs**: Use the backend endpoints
3. **Read the Docs**: Check README.md for detailed info
4. **Customize**: Modify services for your needs
5. **Deploy**: Use Docker Compose for production

## Support

- **Documentation**: README.md
- **Email**: platform@myengineering.tech
- **Phone**: (800) 100-2000

---

**🎉 You're all set! Start exploring the platform.**
