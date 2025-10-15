/**
 * Centralized Logging System with HIPAA Compliance
 * Handles audit trails, PHI logging, and CloudWatch integration
 */
export interface LogContext {
    userId?: string;
    patientId?: string;
    action?: string;
    resourceType?: string;
    resourceId?: string;
    ipAddress?: string;
    userAgent?: string;
    phi_accessed?: boolean;
    requestId?: string;
}
/**
 * Log helper functions
 */
export declare function logInfo(message: string, context?: LogContext): void;
export declare function logError(message: string, error?: Error, context?: LogContext): void;
export declare function logWarn(message: string, context?: LogContext): void;
export declare function logDebug(message: string, context?: LogContext): void;
/**
 * Audit log function for HIPAA compliance
 * Logs all PHI access and critical actions
 */
export declare function logAudit(action: string, resourceType: string, resourceId: string, context: LogContext): void;
/**
 * Sanitize sensitive data before logging
 */
export declare function sanitizeForLogging(data: any): any;
/**
 * Performance monitoring helper
 */
export declare function logPerformance(operation: string, startTime: number, context?: LogContext): void;
/**
 * Request logging middleware
 */
export declare function requestLogger(req: any, res: any, next: any): void;
/**
 * Error logging helper for Express error handlers
 */
export declare function logExpressError(err: Error, req: any): void;
declare const _default: {
    logInfo: typeof logInfo;
    logError: typeof logError;
    logWarn: typeof logWarn;
    logDebug: typeof logDebug;
    logAudit: typeof logAudit;
    sanitizeForLogging: typeof sanitizeForLogging;
    logPerformance: typeof logPerformance;
    requestLogger: typeof requestLogger;
    logExpressError: typeof logExpressError;
};
export default _default;
//# sourceMappingURL=logger.d.ts.map