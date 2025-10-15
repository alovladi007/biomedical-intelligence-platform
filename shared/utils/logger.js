"use strict";
/**
 * Centralized Logging System with HIPAA Compliance
 * Handles audit trails, PHI logging, and CloudWatch integration
 */
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.logInfo = logInfo;
exports.logError = logError;
exports.logWarn = logWarn;
exports.logDebug = logDebug;
exports.logAudit = logAudit;
exports.sanitizeForLogging = sanitizeForLogging;
exports.logPerformance = logPerformance;
exports.requestLogger = requestLogger;
exports.logExpressError = logExpressError;
const winston_1 = __importDefault(require("winston"));
const aws_1 = require("../config/aws");
// Custom log levels for healthcare
const customLevels = {
    levels: {
        error: 0,
        warn: 1,
        info: 2,
        audit: 3,
        debug: 4,
    },
    colors: {
        error: 'red',
        warn: 'yellow',
        info: 'green',
        audit: 'blue',
        debug: 'gray',
    },
};
// Winston logger configuration
const logger = winston_1.default.createLogger({
    levels: customLevels.levels,
    format: winston_1.default.format.combine(winston_1.default.format.timestamp({ format: 'YYYY-MM-DD HH:mm:ss.SSS' }), winston_1.default.format.errors({ stack: true }), winston_1.default.format.splat(), winston_1.default.format.json()),
    defaultMeta: {
        service: 'biomedical-platform',
        environment: process.env.NODE_ENV || 'development',
    },
    transports: [
        // Console transport for development
        new winston_1.default.transports.Console({
            level: process.env.NODE_ENV === 'production' ? 'info' : 'debug',
            format: winston_1.default.format.combine(winston_1.default.format.colorize(), winston_1.default.format.printf(({ timestamp, level, message, ...meta }) => {
                return `${timestamp} [${level}]: ${message} ${Object.keys(meta).length ? JSON.stringify(meta, null, 2) : ''}`;
            })),
        }),
        // File transport for all logs
        new winston_1.default.transports.File({
            filename: 'logs/error.log',
            level: 'error',
            maxsize: 10485760, // 10MB
            maxFiles: 10,
        }),
        new winston_1.default.transports.File({
            filename: 'logs/combined.log',
            maxsize: 10485760,
            maxFiles: 30,
        }),
        // Separate file for audit logs (HIPAA requirement)
        new winston_1.default.transports.File({
            filename: 'logs/audit.log',
            level: 'audit',
            maxsize: 10485760,
            maxFiles: 365, // Keep audit logs for 1 year locally
        }),
    ],
});
winston_1.default.addColors(customLevels.colors);
/**
 * Log helper functions
 */
function logInfo(message, context) {
    logger.info(message, context);
}
function logError(message, error, context) {
    logger.error(message, {
        ...context,
        error: error?.message,
        stack: error?.stack,
    });
}
function logWarn(message, context) {
    logger.warn(message, context);
}
function logDebug(message, context) {
    logger.debug(message, context);
}
/**
 * Audit log function for HIPAA compliance
 * Logs all PHI access and critical actions
 */
function logAudit(action, resourceType, resourceId, context) {
    const auditEntry = {
        timestamp: new Date().toISOString(),
        action,
        resourceType,
        resourceId,
        ...context,
        level: 'audit',
    };
    logger.log('audit', 'AUDIT_TRAIL', auditEntry);
    // Also write to database for long-term retention
    writeAuditToDatabase(auditEntry).catch((error) => {
        logger.error('Failed to write audit log to database', { error: error.message });
    });
    // Upload to S3 for immutable storage (HIPAA requirement)
    if (process.env.NODE_ENV === 'production') {
        uploadAuditLogToS3(auditEntry).catch((error) => {
            logger.error('Failed to upload audit log to S3', { error: error.message });
        });
    }
}
/**
 * Write audit log to TimescaleDB
 */
async function writeAuditToDatabase(auditEntry) {
    const { query } = require('../config/database');
    await query(`INSERT INTO audit_logs (
      timestamp, user_id, patient_id, action, resource_type, resource_id,
      ip_address, user_agent, phi_accessed, request_id, details
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)`, [
        auditEntry.timestamp,
        auditEntry.userId || null,
        auditEntry.patientId || null,
        auditEntry.action,
        auditEntry.resourceType,
        auditEntry.resourceId,
        auditEntry.ipAddress || null,
        auditEntry.userAgent || null,
        auditEntry.phi_accessed || false,
        auditEntry.requestId || null,
        JSON.stringify(auditEntry),
    ]);
}
/**
 * Upload audit log to S3 for immutable storage
 */
async function uploadAuditLogToS3(auditEntry) {
    const date = new Date();
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hour = String(date.getHours()).padStart(2, '0');
    const key = `audit-logs/${year}/${month}/${day}/${hour}/${auditEntry.requestId || Date.now()}.json`;
    await (0, aws_1.uploadToS3)(aws_1.s3Buckets.auditLogs, key, JSON.stringify(auditEntry, null, 2));
}
/**
 * Sanitize sensitive data before logging
 */
function sanitizeForLogging(data) {
    const sensitiveFields = [
        'password',
        'token',
        'apiKey',
        'secret',
        'ssn',
        'creditCard',
        'medicalRecordNumber',
    ];
    if (typeof data !== 'object' || data === null) {
        return data;
    }
    const sanitized = { ...data };
    for (const field of sensitiveFields) {
        if (field in sanitized) {
            sanitized[field] = '***REDACTED***';
        }
    }
    // Recursively sanitize nested objects
    for (const key in sanitized) {
        if (typeof sanitized[key] === 'object' && sanitized[key] !== null) {
            sanitized[key] = sanitizeForLogging(sanitized[key]);
        }
    }
    return sanitized;
}
/**
 * Performance monitoring helper
 */
function logPerformance(operation, startTime, context) {
    const duration = Date.now() - startTime;
    logger.info(`Performance: ${operation}`, {
        ...context,
        duration_ms: duration,
        operation,
    });
    // Alert if operation takes too long
    if (duration > 5000) {
        logger.warn(`Slow operation detected: ${operation}`, {
            ...context,
            duration_ms: duration,
        });
    }
}
/**
 * Request logging middleware
 */
function requestLogger(req, res, next) {
    const startTime = Date.now();
    const requestId = req.headers['x-request-id'] || `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    req.requestId = requestId;
    req.startTime = startTime;
    // Log incoming request
    logInfo('Incoming request', {
        requestId,
        method: req.method,
        url: req.url,
        ipAddress: req.ip,
        userAgent: req.get('user-agent'),
        userId: req.user?.id,
    });
    // Log response
    res.on('finish', () => {
        const duration = Date.now() - startTime;
        logInfo('Request completed', {
            requestId,
            method: req.method,
            url: req.url,
            statusCode: res.statusCode,
            duration_ms: duration,
            userId: req.user?.id,
        });
        // If PHI was accessed, create audit log
        if (req.phi_accessed) {
            logAudit(`${req.method} ${req.url}`, req.resourceType || 'unknown', req.resourceId || 'unknown', {
                requestId,
                userId: req.user?.id,
                patientId: req.patientId,
                ipAddress: req.ip,
                userAgent: req.get('user-agent'),
                phi_accessed: true,
            });
        }
    });
    next();
}
/**
 * Error logging helper for Express error handlers
 */
function logExpressError(err, req) {
    logError('Express error', err, {
        requestId: req.requestId,
        method: req.method,
        url: req.url,
        userId: req.user?.id,
        ipAddress: req.ip,
    });
}
exports.default = {
    logInfo,
    logError,
    logWarn,
    logDebug,
    logAudit,
    sanitizeForLogging,
    logPerformance,
    requestLogger,
    logExpressError,
};
//# sourceMappingURL=logger.js.map