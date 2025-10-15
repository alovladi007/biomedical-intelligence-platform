/**
 * Database Configuration for TimescaleDB and PostgreSQL
 * Handles connections, pooling, and HIPAA-compliant encryption
 */
import { PoolConfig } from 'pg';
export interface DatabaseConfig extends PoolConfig {
    host: string;
    port: number;
    database: string;
    user: string;
    password: string;
    ssl: boolean | {
        rejectUnauthorized: boolean;
        ca?: string;
        key?: string;
        cert?: string;
    };
    max: number;
    idleTimeoutMillis: number;
    connectionTimeoutMillis: number;
}
export declare const databaseConfig: DatabaseConfig;
export declare const pool: any;
export declare function testDatabaseConnection(): Promise<boolean>;
export declare function initializeTimescaleDB(): Promise<void>;
export declare function query(text: string, params?: any[]): Promise<any>;
export declare function transaction(callback: (client: any) => Promise<void>): Promise<void>;
export declare function closeDatabaseConnection(): Promise<void>;
//# sourceMappingURL=database.d.ts.map