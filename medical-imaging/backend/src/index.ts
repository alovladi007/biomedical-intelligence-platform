/**
 * Medical Imaging AI Backend
 * DICOM Processing and AI Inference Service
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
const PORT = process.env.PORT || 5002;

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Security
app.use(helmet());

// CORS
const corsOptions = {
  origin: (process.env.CORS_ORIGINS || 'http://localhost:3002').split(','),
  credentials: true,
};
app.use(cors(corsOptions));

// Body parsing
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Compression
app.use(compression());

// Logging
app.use(morgan('combined'));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 50, // Lower limit for image processing
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
    service: 'medical-imaging',
    version: '1.0.0',
    mode: process.env.DEMO_MODE === 'true' ? 'demo' : 'production',
  });
});

// Root endpoint
app.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'Medical Imaging AI',
    description: 'DICOM Processing and AI Inference Platform',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      studies: '/api/v1/studies',
      analyze: '/api/v1/analyze',
      reports: '/api/v1/reports',
      triage: '/api/v1/triage',
    },
  });
});

// Mock API endpoints for demo
app.get('/api/v1/studies', (_req: Request, res: Response) => {
  res.json({
    success: true,
    studies: [
      {
        id: 'STU-001',
        patientId: 'P001',
        patientName: 'Robert Chen',
        modality: 'CT',
        bodyPart: 'Chest',
        studyDate: '2025-10-20',
        status: 'analyzed',
        findings: 'No acute findings',
        priority: 'routine',
      },
      {
        id: 'STU-002',
        patientId: 'P002',
        patientName: 'Emma Davis',
        modality: 'MRI',
        bodyPart: 'Brain',
        studyDate: '2025-10-19',
        status: 'pending',
        findings: null,
        priority: 'urgent',
      },
      {
        id: 'STU-003',
        patientId: 'P003',
        patientName: 'Michael Brown',
        modality: 'X-Ray',
        bodyPart: 'Abdomen',
        studyDate: '2025-10-18',
        status: 'analyzed',
        findings: 'Mild degenerative changes',
        priority: 'routine',
      },
    ],
    total: 3,
  });
});

app.post('/api/v1/analyze', (req: Request, res: Response) => {
  const { studyId, imageData } = req.body;
  
  // Mock AI analysis with Grad-CAM
  res.json({
    success: true,
    analysis: {
      studyId: studyId || `STU-${Date.now()}`,
      predictions: [
        {
          finding: 'Normal',
          confidence: 0.89,
          location: { x: 120, y: 150, width: 80, height: 90 },
        },
        {
          finding: 'Possible nodule',
          confidence: 0.12,
          location: { x: 200, y: 100, width: 40, height: 45 },
        },
      ],
      gradcam: {
        heatmapUrl: '/api/v1/gradcam/heatmap-12345.png',
        overlayUrl: '/api/v1/gradcam/overlay-12345.png',
      },
      triage: {
        priority: 'routine',
        urgencyScore: 0.15,
        recommendation: 'Standard radiologist review',
      },
      processingTime: 2.4,
      timestamp: new Date().toISOString(),
    },
  });
});

app.get('/api/v1/reports', (_req: Request, res: Response) => {
  res.json({
    success: true,
    reports: [
      {
        id: 'RPT-001',
        studyId: 'STU-001',
        radiologist: 'Dr. Sarah Martinez',
        findings: 'No acute cardiopulmonary abnormality',
        impression: 'Unremarkable chest CT',
        date: '2025-10-20',
        status: 'finalized',
      },
      {
        id: 'RPT-002',
        studyId: 'STU-003',
        radiologist: 'Dr. James Wilson',
        findings: 'Mild degenerative changes in lumbar spine',
        impression: 'Age-appropriate findings',
        date: '2025-10-18',
        status: 'finalized',
      },
    ],
  });
});

app.get('/api/v1/triage', (_req: Request, res: Response) => {
  res.json({
    success: true,
    triage: {
      urgent: [
        {
          studyId: 'STU-002',
          priority: 'urgent',
          urgencyScore: 0.92,
          reason: 'Possible acute finding',
          waitTime: 15,
        },
      ],
      routine: [
        {
          studyId: 'STU-001',
          priority: 'routine',
          urgencyScore: 0.15,
          reason: 'Normal study',
          waitTime: 240,
        },
      ],
    },
  });
});

app.get('/api/v1/analytics', (_req: Request, res: Response) => {
  res.json({
    success: true,
    analytics: {
      totalStudies: 8765,
      studiesAnalyzed: 8234,
      avgAccuracy: 0.94,
      avgProcessingTime: 2.1,
      urgentCases: 87,
      modalityBreakdown: {
        'CT': 3245,
        'MRI': 2876,
        'X-Ray': 2654,
      },
    },
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
  console.log('🔬 Medical Imaging AI service started successfully');
  console.log(`   Port: ${PORT}`);
  console.log(`   Mode: ${process.env.DEMO_MODE === 'true' ? 'Demo' : 'Production'}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🏥 API Base: http://localhost:${PORT}/api/v1`);
});

export default app;
