/**
 * MYNX NatalCare Backend
 * Maternal Health Monitoring Service
 */

import express, { Application, Request, Response } from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import morgan from 'morgan';
import rateLimit from 'express-rate-limit';
import { config } from 'dotenv';

// Load environment variables
config();

const app: Application = express();
const PORT = process.env.PORT || 5006;

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Security
app.use(helmet());

// CORS
const corsOptions = {
  origin: (process.env.CORS_ORIGINS || 'http://localhost:3006').split(','),
  credentials: true,
};
app.use(cors(corsOptions));

// Body parsing
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true }));

// Compression
app.use(compression());

// Logging
app.use(morgan('combined'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100,
});
app.use('/api', limiter);

// ============================================================================
// ROUTES
// ============================================================================

// Health check
app.get('/health', (_req: Request, res: Response) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'mynx-natalcare',
    version: '1.0.0',
    mode: process.env.DEMO_MODE === 'true' ? 'demo' : 'production',
  });
});

// Root endpoint
app.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'MYNX NatalCare',
    description: 'Maternal Health Monitoring Platform',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      patients: '/api/v1/patients',
      appointments: '/api/v1/appointments',
      vitals: '/api/v1/vitals',
      alerts: '/api/v1/alerts',
    },
  });
});

// Mock API endpoints for demo
app.get('/api/v1/patients', (_req: Request, res: Response) => {
  res.json({
    success: true,
    patients: [
      {
        id: '1',
        name: 'Sarah Johnson',
        age: 28,
        gestationalWeek: 24,
        dueDate: '2025-03-15',
        riskLevel: 'low',
      },
      {
        id: '2',
        name: 'Maria Garcia',
        age: 32,
        gestationalWeek: 36,
        dueDate: '2025-01-28',
        riskLevel: 'moderate',
      },
    ],
    total: 2,
  });
});

app.get('/api/v1/appointments', (_req: Request, res: Response) => {
  res.json({
    success: true,
    appointments: [
      {
        id: '1',
        patientId: '1',
        patientName: 'Sarah Johnson',
        date: '2025-10-20',
        time: '10:00 AM',
        type: 'Prenatal Checkup',
        status: 'scheduled',
      },
      {
        id: '2',
        patientId: '2',
        patientName: 'Maria Garcia',
        date: '2025-10-18',
        time: '2:00 PM',
        type: 'Ultrasound',
        status: 'confirmed',
      },
    ],
    total: 2,
  });
});

app.get('/api/v1/vitals', (_req: Request, res: Response) => {
  res.json({
    success: true,
    vitals: [
      {
        id: '1',
        patientId: '1',
        timestamp: new Date().toISOString(),
        bloodPressure: '118/76',
        heartRate: 78,
        weight: 165,
        temperature: 98.6,
      },
    ],
  });
});

app.get('/api/v1/alerts', (_req: Request, res: Response) => {
  res.json({
    success: true,
    alerts: [
      {
        id: '1',
        patientId: '2',
        severity: 'medium',
        message: 'Elevated blood pressure detected',
        timestamp: new Date().toISOString(),
        acknowledged: false,
      },
    ],
  });
});

// 404 handler
app.use((_req: Request, res: Response) => {
  res.status(404).json({
    success: false,
    error: 'Endpoint not found',
  });
});

// ============================================================================
// SERVER STARTUP
// ============================================================================

app.listen(PORT, () => {
  console.log('🤰 MYNX NatalCare service started successfully');
  console.log(`   Port: ${PORT}`);
  console.log(`   Mode: ${process.env.DEMO_MODE === 'true' ? 'Demo' : 'Production'}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🏥 API Base: http://localhost:${PORT}/api/v1`);
});

export default app;
