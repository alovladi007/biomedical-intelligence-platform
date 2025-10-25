/**
 * Biosensing Technology Backend
 * Real-time Health Monitoring Service
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
const PORT = process.env.PORT || 5003;

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Security
app.use(helmet());

// CORS
const corsOptions = {
  origin: (process.env.CORS_ORIGINS || 'http://localhost:3003').split(','),
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
  max: 200, // Higher limit for sensor data
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
    service: 'biosensing',
    version: '1.0.0',
    mode: process.env.DEMO_MODE === 'true' ? 'demo' : 'production',
  });
});

// Root endpoint
app.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'Biosensing Technology',
    description: 'Real-time Health Monitoring Platform',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      devices: '/api/v1/devices',
      readings: '/api/v1/readings',
      alerts: '/api/v1/alerts',
      stream: '/api/v1/stream',
    },
  });
});

// Mock API endpoints for demo
app.get('/api/v1/devices', (_req: Request, res: Response) => {
  res.json({
    success: true,
    devices: [
      {
        id: 'DEV-001',
        patientId: 'P001',
        patientName: 'Alice Cooper',
        type: 'Continuous Glucose Monitor',
        manufacturer: 'Dexcom',
        model: 'G7',
        status: 'active',
        lastReading: '2025-10-24T14:30:00Z',
        batteryLevel: 85,
      },
      {
        id: 'DEV-002',
        patientId: 'P002',
        patientName: 'Bob Wilson',
        type: 'Blood Pressure Monitor',
        manufacturer: 'Omron',
        model: 'Evolv',
        status: 'active',
        lastReading: '2025-10-24T13:15:00Z',
        batteryLevel: 62,
      },
      {
        id: 'DEV-003',
        patientId: 'P003',
        patientName: 'Carol Martinez',
        type: 'Heart Rate Monitor',
        manufacturer: 'Polar',
        model: 'H10',
        status: 'offline',
        lastReading: '2025-10-23T20:00:00Z',
        batteryLevel: 15,
      },
    ],
    total: 3,
  });
});

app.get('/api/v1/readings', (req: Request, res: Response) => {
  const { deviceId, startTime, endTime } = req.query;
  
  // Mock sensor readings
  const readings = [];
  const now = new Date();
  
  for (let i = 0; i < 20; i++) {
    const timestamp = new Date(now.getTime() - i * 5 * 60 * 1000); // Every 5 minutes
    readings.push({
      id: `READ-${Date.now()}-${i}`,
      deviceId: deviceId || 'DEV-001',
      timestamp: timestamp.toISOString(),
      value: 95 + Math.random() * 30,
      unit: 'mg/dL',
      quality: 'good',
    });
  }
  
  res.json({
    success: true,
    readings: readings.reverse(),
    total: readings.length,
  });
});

app.post('/api/v1/readings', (req: Request, res: Response) => {
  const { deviceId, value, unit } = req.body;
  
  res.json({
    success: true,
    reading: {
      id: `READ-${Date.now()}`,
      deviceId,
      value,
      unit,
      timestamp: new Date().toISOString(),
      status: 'received',
    },
  });
});

app.get('/api/v1/alerts', (_req: Request, res: Response) => {
  res.json({
    success: true,
    alerts: [
      {
        id: 'ALT-001',
        deviceId: 'DEV-001',
        patientId: 'P001',
        patientName: 'Alice Cooper',
        severity: 'high',
        type: 'threshold',
        message: 'Glucose level above target range',
        value: 185,
        threshold: 180,
        timestamp: '2025-10-24T14:30:00Z',
        acknowledged: false,
      },
      {
        id: 'ALT-002',
        deviceId: 'DEV-003',
        patientId: 'P003',
        patientName: 'Carol Martinez',
        severity: 'medium',
        type: 'connection',
        message: 'Device offline for 18 hours',
        timestamp: '2025-10-24T08:00:00Z',
        acknowledged: false,
      },
    ],
    total: 2,
  });
});

app.post('/api/v1/alerts/:id/acknowledge', (req: Request, res: Response) => {
  const { id } = req.params;
  
  res.json({
    success: true,
    alert: {
      id,
      acknowledged: true,
      acknowledgedBy: 'Dr. Smith',
      acknowledgedAt: new Date().toISOString(),
    },
  });
});

app.get('/api/v1/analytics', (_req: Request, res: Response) => {
  res.json({
    success: true,
    analytics: {
      totalDevices: 1247,
      activeDevices: 1198,
      totalReadings: 2847653,
      avgReadingsPerDay: 124532,
      activeAlerts: 23,
      deviceTypes: {
        'Glucose Monitor': 423,
        'Blood Pressure': 387,
        'Heart Rate': 234,
        'Pulse Oximeter': 203,
      },
    },
  });
});

// WebSocket simulation endpoint
app.get('/api/v1/stream/connect', (_req: Request, res: Response) => {
  res.json({
    success: true,
    message: 'WebSocket connection info',
    endpoint: 'ws://localhost:5003/stream',
    protocols: ['mqtt', 'websocket'],
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
  console.log('📡 Biosensing Technology service started successfully');
  console.log(`   Port: ${PORT}`);
  console.log(`   Mode: ${process.env.DEMO_MODE === 'true' ? 'Demo' : 'Production'}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🏥 API Base: http://localhost:${PORT}/api/v1`);
});

export default app;
