/**
 * BioTensor Labs Backend
 * MLOps and Model Management Service
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
const PORT = process.env.PORT || 5005;

// ============================================================================
// MIDDLEWARE
// ============================================================================

// Security
app.use(helmet());

// CORS
const corsOptions = {
  origin: (process.env.CORS_ORIGINS || 'http://localhost:3005').split(','),
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
    service: 'biotensor-labs',
    version: '1.0.0',
    mode: process.env.DEMO_MODE === 'true' ? 'demo' : 'production',
  });
});

// Root endpoint
app.get('/', (_req: Request, res: Response) => {
  res.json({
    service: 'BioTensor Labs',
    description: 'MLOps and Model Management Platform',
    version: '1.0.0',
    status: 'running',
    endpoints: {
      health: '/health',
      experiments: '/api/v1/experiments',
      models: '/api/v1/models',
      deployments: '/api/v1/deployments',
      metrics: '/api/v1/metrics',
    },
  });
});

// Mock API endpoints for demo
app.get('/api/v1/experiments', (_req: Request, res: Response) => {
  res.json({
    success: true,
    experiments: [
      {
        id: 'EXP-001',
        name: 'diabetes-prediction-v3',
        description: 'Improved diabetes risk prediction model',
        framework: 'TensorFlow',
        status: 'completed',
        accuracy: 0.94,
        loss: 0.123,
        startTime: '2025-10-20T10:00:00Z',
        endTime: '2025-10-20T14:30:00Z',
        parameters: {
          learning_rate: 0.001,
          batch_size: 32,
          epochs: 100,
        },
      },
      {
        id: 'EXP-002',
        name: 'cardiac-imaging-classifier',
        description: 'CNN for cardiac MRI classification',
        framework: 'PyTorch',
        status: 'running',
        accuracy: 0.89,
        loss: 0.187,
        startTime: '2025-10-24T09:00:00Z',
        endTime: null,
        parameters: {
          learning_rate: 0.0001,
          batch_size: 16,
          epochs: 200,
        },
      },
      {
        id: 'EXP-003',
        name: 'drug-response-predictor',
        description: 'XGBoost model for drug response prediction',
        framework: 'XGBoost',
        status: 'completed',
        accuracy: 0.87,
        loss: 0.234,
        startTime: '2025-10-22T08:00:00Z',
        endTime: '2025-10-22T11:45:00Z',
        parameters: {
          max_depth: 6,
          learning_rate: 0.1,
          n_estimators: 100,
        },
      },
    ],
    total: 3,
  });
});

app.post('/api/v1/experiments', (req: Request, res: Response) => {
  const { name, framework, parameters } = req.body;
  
  res.json({
    success: true,
    experiment: {
      id: `EXP-${Date.now()}`,
      name,
      framework,
      parameters,
      status: 'queued',
      createdAt: new Date().toISOString(),
    },
  });
});

app.get('/api/v1/models', (_req: Request, res: Response) => {
  res.json({
    success: true,
    models: [
      {
        id: 'MDL-001',
        name: 'diabetes-risk-v2',
        version: '2.1.0',
        framework: 'TensorFlow',
        type: 'classification',
        accuracy: 0.94,
        status: 'production',
        deployedAt: '2025-10-15T12:00:00Z',
        predictions: 12543,
        avgLatency: 45,
      },
      {
        id: 'MDL-002',
        name: 'cardiovascular-risk-v3',
        version: '3.0.1',
        framework: 'PyTorch',
        type: 'regression',
        accuracy: 0.91,
        status: 'production',
        deployedAt: '2025-10-10T14:30:00Z',
        predictions: 9876,
        avgLatency: 52,
      },
      {
        id: 'MDL-003',
        name: 'cancer-screening-v1',
        version: '1.2.0',
        framework: 'scikit-learn',
        type: 'classification',
        accuracy: 0.89,
        status: 'staging',
        deployedAt: '2025-10-20T09:00:00Z',
        predictions: 543,
        avgLatency: 38,
      },
    ],
    total: 3,
  });
});

app.post('/api/v1/models/:id/deploy', (req: Request, res: Response) => {
  const { id } = req.params;
  const { environment } = req.body;
  
  res.json({
    success: true,
    deployment: {
      id: `DEP-${Date.now()}`,
      modelId: id,
      environment: environment || 'staging',
      status: 'deploying',
      startedAt: new Date().toISOString(),
      estimatedTime: 300,
    },
  });
});

app.get('/api/v1/deployments', (_req: Request, res: Response) => {
  res.json({
    success: true,
    deployments: [
      {
        id: 'DEP-001',
        modelId: 'MDL-001',
        modelName: 'diabetes-risk-v2',
        environment: 'production',
        status: 'active',
        instances: 3,
        cpu: 45,
        memory: 62,
        requests: 12543,
        avgLatency: 45,
        errorRate: 0.002,
      },
      {
        id: 'DEP-002',
        modelId: 'MDL-002',
        modelName: 'cardiovascular-risk-v3',
        environment: 'production',
        status: 'active',
        instances: 2,
        cpu: 38,
        memory: 55,
        requests: 9876,
        avgLatency: 52,
        errorRate: 0.001,
      },
      {
        id: 'DEP-003',
        modelId: 'MDL-003',
        modelName: 'cancer-screening-v1',
        environment: 'staging',
        status: 'active',
        instances: 1,
        cpu: 22,
        memory: 41,
        requests: 543,
        avgLatency: 38,
        errorRate: 0.005,
      },
    ],
    total: 3,
  });
});

app.get('/api/v1/metrics/:modelId', (req: Request, res: Response) => {
  const { modelId } = req.params;
  
  // Generate mock time-series metrics
  const metrics = [];
  const now = new Date();
  
  for (let i = 0; i < 24; i++) {
    const timestamp = new Date(now.getTime() - i * 60 * 60 * 1000); // Hourly
    metrics.push({
      timestamp: timestamp.toISOString(),
      requests: Math.floor(400 + Math.random() * 200),
      avgLatency: 40 + Math.random() * 20,
      errorRate: Math.random() * 0.01,
      accuracy: 0.90 + Math.random() * 0.05,
    });
  }
  
  res.json({
    success: true,
    modelId,
    metrics: metrics.reverse(),
  });
});

app.get('/api/v1/analytics', (_req: Request, res: Response) => {
  res.json({
    success: true,
    analytics: {
      totalExperiments: 147,
      activeExperiments: 8,
      totalModels: 34,
      productionModels: 12,
      totalPredictions: 2847653,
      avgModelAccuracy: 0.92,
      avgInferenceLatency: 48,
      frameworks: {
        'TensorFlow': 15,
        'PyTorch': 12,
        'scikit-learn': 7,
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
  console.log('🧪 BioTensor Labs service started successfully');
  console.log(`   Port: ${PORT}`);
  console.log(`   Mode: ${process.env.DEMO_MODE === 'true' ? 'Demo' : 'Production'}`);
  console.log(`📊 Health check: http://localhost:${PORT}/health`);
  console.log(`🏥 API Base: http://localhost:${PORT}/api/v1`);
});

export default app;
