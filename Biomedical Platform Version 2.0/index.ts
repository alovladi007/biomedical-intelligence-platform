/**
 * AI Diagnostics Backend
 * ML-based Medical Diagnostics Service
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
const PORT = process.env.PORT || 5001;

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Security
app.use(helmet());

// CORS
const corsOptions = {
  origin: (process.env.CORS_ORIGINS || 'http://localhost:3007').split(','),
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
    service: 'ai-diagnostics',
    version: '1.0.0',
    mode: process.env.DEMO_MODE === 'true' ? 'demo' : 'production',
  });
});

// Root endpoint
app.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'AI Diagnostics',
    description: 'ML-based Medical Diagnostics Platform',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      diagnostics: '/api/v1/diagnostics',
      predictions: '/api/v1/predictions',
      models: '/api/v1/models',
      analytics: '/api/v1/analytics',
    },
  });
});

// Mock API endpoints for demo
app.get('/api/v1/diagnostics', (_req: Request, res: Response) => {
  res.json({
    success: true,
    diagnostics: [
      {
        id: '1',
        patientId: 'P001',
        patientName: 'John Smith',
        condition: 'Type 2 Diabetes',
        riskScore: 0.78,
        confidence: 0.92,
        date: '2025-10-20',
        status: 'pending-review',
      },
      {
        id: '2',
        patientId: 'P002',
        patientName: 'Mary Johnson',
        condition: 'Hypertension',
        riskScore: 0.65,
        confidence: 0.88,
        date: '2025-10-19',
        status: 'confirmed',
      },
      {
        id: '3',
        patientId: 'P003',
        patientName: 'David Lee',
        condition: 'Cardiovascular Disease',
        riskScore: 0.82,
        confidence: 0.95,
        date: '2025-10-18',
        status: 'under-treatment',
      },
    ],
    total: 3,
  });
});

app.post('/api/v1/diagnostics/analyze', (req: Request, res: Response) => {
  const { patientData } = req.body;
  
  // Mock AI analysis
  res.json({
    success: true,
    analysis: {
      id: `DIAG-${Date.now()}`,
      predictions: [
        {
          condition: 'Type 2 Diabetes',
          probability: 0.78,
          riskLevel: 'high',
          features: ['elevated glucose', 'BMI > 30', 'family history'],
        },
        {
          condition: 'Hypertension',
          probability: 0.45,
          riskLevel: 'moderate',
          features: ['blood pressure 140/90', 'age > 50'],
        },
      ],
      recommendations: [
        'Lifestyle modifications recommended',
        'Schedule follow-up in 3 months',
        'Consider medication review',
      ],
      timestamp: new Date().toISOString(),
    },
  });
});

app.get('/api/v1/predictions', (_req: Request, res: Response) => {
  res.json({
    success: true,
    predictions: [
      {
        id: '1',
        model: 'diabetes-risk-v2',
        accuracy: 0.94,
        lastUpdated: '2025-10-15',
        predictions: 1243,
      },
      {
        id: '2',
        model: 'cardiovascular-risk-v3',
        accuracy: 0.91,
        lastUpdated: '2025-10-14',
        predictions: 987,
      },
    ],
  });
});

app.get('/api/v1/models', (_req: Request, res: Response) => {
  res.json({
    success: true,
    models: [
      {
        id: '1',
        name: 'diabetes-risk-v2',
        type: 'classification',
        framework: 'TensorFlow',
        accuracy: 0.94,
        status: 'production',
        version: '2.1.0',
      },
      {
        id: '2',
        name: 'cardiovascular-risk-v3',
        type: 'risk-prediction',
        framework: 'PyTorch',
        accuracy: 0.91,
        status: 'production',
        version: '3.0.1',
      },
      {
        id: '3',
        name: 'cancer-screening-v1',
        type: 'classification',
        framework: 'scikit-learn',
        accuracy: 0.89,
        status: 'staging',
        version: '1.2.0',
      },
    ],
  });
});

app.get('/api/v1/analytics', (_req: Request, res: Response) => {
  res.json({
    success: true,
    analytics: {
      totalDiagnostics: 12543,
      accuracyRate: 0.92,
      avgProcessingTime: 1.2,
      activeModels: 8,
      dailyAnalyses: 145,
      topConditions: [
        { name: 'Diabetes', count: 234 },
        { name: 'Hypertension', count: 198 },
        { name: 'Cardiovascular', count: 156 },
      ],
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
  console.log('🧠 AI Diagnostics service started successfully');
  console.log(`   Port: ${PORT}`);
  console.log(`   Mode: ${process.env.DEMO_MODE === 'true' ? 'Demo' : 'Production'}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🏥 API Base: http://localhost:${PORT}/api/v1`);
});

export default app;
