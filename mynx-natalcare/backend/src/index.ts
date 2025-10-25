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
        bloodType: 'A+',
        lastVisit: '2025-10-10',
        nextAppointment: '2025-11-05',
        provider: 'Dr. Emily Chen',
        complications: [],
        pregnancy: {
          gravida: 2,
          para: 1,
          abortions: 0,
          living: 1,
        },
      },
      {
        id: '2',
        name: 'Maria Garcia',
        age: 32,
        gestationalWeek: 36,
        dueDate: '2025-01-28',
        riskLevel: 'moderate',
        bloodType: 'O+',
        lastVisit: '2025-10-18',
        nextAppointment: '2025-10-25',
        provider: 'Dr. Sarah Williams',
        complications: ['Gestational Diabetes'],
        pregnancy: {
          gravida: 3,
          para: 2,
          abortions: 0,
          living: 2,
        },
      },
      {
        id: '3',
        name: 'Jennifer Lee',
        age: 25,
        gestationalWeek: 12,
        dueDate: '2025-05-20',
        riskLevel: 'low',
        bloodType: 'B+',
        lastVisit: '2025-10-15',
        nextAppointment: '2025-11-12',
        provider: 'Dr. Emily Chen',
        complications: [],
        pregnancy: {
          gravida: 1,
          para: 0,
          abortions: 0,
          living: 0,
        },
      },
      {
        id: '4',
        name: 'Amanda Brown',
        age: 35,
        gestationalWeek: 30,
        dueDate: '2025-02-10',
        riskLevel: 'high',
        bloodType: 'AB-',
        lastVisit: '2025-10-20',
        nextAppointment: '2025-10-27',
        provider: 'Dr. Sarah Williams',
        complications: ['Advanced Maternal Age', 'Hypertension'],
        pregnancy: {
          gravida: 4,
          para: 3,
          abortions: 0,
          living: 3,
        },
      },
      {
        id: '5',
        name: 'Lisa Martinez',
        age: 29,
        gestationalWeek: 18,
        dueDate: '2025-04-05',
        riskLevel: 'low',
        bloodType: 'O-',
        lastVisit: '2025-10-12',
        nextAppointment: '2025-11-09',
        provider: 'Dr. Emily Chen',
        complications: [],
        pregnancy: {
          gravida: 2,
          para: 1,
          abortions: 0,
          living: 1,
        },
      },
    ],
    total: 5,
  });
});

// Get patient by ID
app.get('/api/v1/patients/:id', (req: Request, res: Response) => {
  const { id } = req.params;
  
  res.json({
    success: true,
    patient: {
      id,
      name: 'Sarah Johnson',
      age: 28,
      dateOfBirth: '1997-03-15',
      gestationalWeek: 24,
      dueDate: '2025-03-15',
      riskLevel: 'low',
      bloodType: 'A+',
      provider: 'Dr. Emily Chen',
      medicalHistory: {
        allergies: ['Penicillin'],
        previousPregnancies: 1,
        complications: [],
        chronicConditions: [],
      },
      currentPregnancy: {
        conception: '2025-06-10',
        lmp: '2025-05-27',
        edd: '2025-03-15',
        gestationalAge: '24 weeks 3 days',
        trimester: 2,
      },
      vitalSigns: [
        {
          date: '2025-10-20',
          bloodPressure: '118/76',
          weight: 165,
          heartRate: 78,
          temperature: 98.6,
        },
        {
          date: '2025-10-10',
          bloodPressure: '120/78',
          weight: 162,
          heartRate: 76,
          temperature: 98.4,
        },
      ],
      labResults: [
        {
          date: '2025-09-15',
          test: 'Glucose Tolerance Test',
          result: 'Normal',
          value: '95 mg/dL',
        },
        {
          date: '2025-08-20',
          test: 'Complete Blood Count',
          result: 'Normal',
          value: 'Hemoglobin 12.5 g/dL',
        },
      ],
      ultrasounds: [
        {
          date: '2025-10-01',
          gestationalAge: '22 weeks',
          fetalWeight: '1.2 lbs',
          findings: 'Normal development',
        },
      ],
    },
  });
});

// Create new patient
app.post('/api/v1/patients', (req: Request, res: Response) => {
  const patientData = req.body;
  
  res.json({
    success: true,
    patient: {
      id: `P${Date.now()}`,
      ...patientData,
      createdAt: new Date().toISOString(),
    },
  });
});

// Update patient
app.put('/api/v1/patients/:id', (req: Request, res: Response) => {
  const { id } = req.params;
  const updates = req.body;
  
  res.json({
    success: true,
    patient: {
      id,
      ...updates,
      updatedAt: new Date().toISOString(),
    },
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
        date: '2025-11-05',
        time: '10:00 AM',
        type: 'Prenatal Checkup',
        provider: 'Dr. Emily Chen',
        status: 'scheduled',
        duration: 30,
        notes: 'Routine 24-week checkup',
      },
      {
        id: '2',
        patientId: '2',
        patientName: 'Maria Garcia',
        date: '2025-10-25',
        time: '2:00 PM',
        type: 'Ultrasound',
        provider: 'Dr. Sarah Williams',
        status: 'confirmed',
        duration: 45,
        notes: '36-week growth scan',
      },
      {
        id: '3',
        patientId: '3',
        patientName: 'Jennifer Lee',
        date: '2025-11-12',
        time: '11:30 AM',
        type: 'First Trimester Screening',
        provider: 'Dr. Emily Chen',
        status: 'scheduled',
        duration: 60,
        notes: 'NT scan and bloodwork',
      },
      {
        id: '4',
        patientId: '4',
        patientName: 'Amanda Brown',
        date: '2025-10-27',
        time: '9:00 AM',
        type: 'High Risk Consultation',
        provider: 'Dr. Sarah Williams',
        status: 'confirmed',
        duration: 45,
        notes: 'BP monitoring and discussion',
      },
    ],
    total: 4,
  });
});

// Schedule appointment
app.post('/api/v1/appointments', (req: Request, res: Response) => {
  const appointmentData = req.body;
  
  res.json({
    success: true,
    appointment: {
      id: `APT${Date.now()}`,
      ...appointmentData,
      status: 'scheduled',
      createdAt: new Date().toISOString(),
    },
  });
});

// Cancel appointment
app.delete('/api/v1/appointments/:id', (req: Request, res: Response) => {
  const { id } = req.params;
  
  res.json({
    success: true,
    message: `Appointment ${id} cancelled successfully`,
  });
});

app.get('/api/v1/vitals', (_req: Request, res: Response) => {
  res.json({
    success: true,
    vitals: [
      {
        id: '1',
        patientId: '1',
        patientName: 'Sarah Johnson',
        timestamp: '2025-10-20T10:30:00Z',
        bloodPressure: { systolic: 118, diastolic: 76 },
        heartRate: 78,
        weight: 165,
        temperature: 98.6,
        fetalHeartRate: 145,
        oxygenSaturation: 98,
      },
      {
        id: '2',
        patientId: '2',
        patientName: 'Maria Garcia',
        timestamp: '2025-10-20T14:15:00Z',
        bloodPressure: { systolic: 138, diastolic: 88 },
        heartRate: 82,
        weight: 178,
        temperature: 98.8,
        fetalHeartRate: 142,
        oxygenSaturation: 97,
      },
      {
        id: '3',
        patientId: '3',
        patientName: 'Jennifer Lee',
        timestamp: '2025-10-20T09:00:00Z',
        bloodPressure: { systolic: 112, diastolic: 72 },
        heartRate: 74,
        weight: 142,
        temperature: 98.4,
        fetalHeartRate: 148,
        oxygenSaturation: 99,
      },
    ],
  });
});

// Record vital signs
app.post('/api/v1/vitals', (req: Request, res: Response) => {
  const vitalData = req.body;
  
  res.json({
    success: true,
    vital: {
      id: `VIT${Date.now()}`,
      ...vitalData,
      timestamp: new Date().toISOString(),
    },
  });
});

app.get('/api/v1/alerts', (_req: Request, res: Response) => {
  res.json({
    success: true,
    alerts: [
      {
        id: '1',
        patientId: '2',
        patientName: 'Maria Garcia',
        severity: 'high',
        type: 'Vital Sign Alert',
        message: 'Elevated blood pressure detected: 138/88 mmHg',
        timestamp: '2025-10-20T14:15:00Z',
        acknowledged: false,
        action: 'Contact patient for follow-up',
      },
      {
        id: '2',
        patientId: '4',
        patientName: 'Amanda Brown',
        severity: 'medium',
        type: 'Appointment Reminder',
        message: 'High-risk consultation scheduled for tomorrow',
        timestamp: '2025-10-26T08:00:00Z',
        acknowledged: false,
        action: 'Confirm appointment',
      },
      {
        id: '3',
        patientId: '1',
        patientName: 'Sarah Johnson',
        severity: 'low',
        type: 'Lab Results',
        message: 'Lab results available for review',
        timestamp: '2025-10-19T16:30:00Z',
        acknowledged: true,
        action: 'Review results',
      },
    ],
  });
});

// Acknowledge alert
app.post('/api/v1/alerts/:id/acknowledge', (req: Request, res: Response) => {
  const { id } = req.params;
  
  res.json({
    success: true,
    message: `Alert ${id} acknowledged`,
  });
});

// Analytics
app.get('/api/v1/analytics', (_req: Request, res: Response) => {
  res.json({
    success: true,
    analytics: {
      totalPatients: 247,
      activePregnancies: 198,
      appointmentsToday: 12,
      appointmentsThisWeek: 67,
      highRiskPatients: 23,
      averageGestationalAge: 22.5,
      upcomingDeliveries: {
        thisWeek: 3,
        thisMonth: 18,
      },
      trimesterBreakdown: [
        { trimester: 1, count: 45, percentage: 23 },
        { trimester: 2, count: 87, percentage: 44 },
        { trimester: 3, count: 66, percentage: 33 },
      ],
      riskLevels: [
        { level: 'low', count: 156, percentage: 79 },
        { level: 'moderate', count: 35, percentage: 18 },
        { level: 'high', count: 7, percentage: 3 },
      ],
    },
  });
});

// Educational resources
app.get('/api/v1/resources', (_req: Request, res: Response) => {
  res.json({
    success: true,
    resources: [
      {
        id: '1',
        title: 'First Trimester Care',
        category: 'Education',
        description: 'Essential information for your first trimester',
        url: '/resources/first-trimester',
      },
      {
        id: '2',
        title: 'Nutrition During Pregnancy',
        category: 'Wellness',
        description: 'Healthy eating guide for expecting mothers',
        url: '/resources/nutrition',
      },
      {
        id: '3',
        title: 'Labor and Delivery',
        category: 'Preparation',
        description: 'What to expect during labor',
        url: '/resources/labor-delivery',
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
