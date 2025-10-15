/**
 * AWS Services Configuration
 * Handles S3, KMS, EKS, RDS, CloudTrail, and other AWS services
 */
export declare const awsConfig: {
    region: string;
    credentials: {
        accessKeyId: string;
        secretAccessKey: string;
    };
};
export declare const s3Client: any;
export declare const kmsClient: any;
export declare const eksClient: any;
export declare const rdsClient: any;
export declare const cloudTrailClient: any;
export declare const s3Buckets: {
    imaging: string;
    features: string;
    models: string;
    exports: string;
    auditLogs: string;
    backups: string;
};
export declare const kmsKeyId: string;
/**
 * Upload file to S3 with server-side encryption using KMS
 */
export declare function uploadToS3(bucket: string, key: string, data: Buffer | string, metadata?: Record<string, string>): Promise<string>;
/**
 * Download file from S3
 */
export declare function downloadFromS3(bucket: string, key: string): Promise<Buffer>;
/**
 * Encrypt data using AWS KMS
 */
export declare function encryptData(plaintext: Buffer | string): Promise<{
    ciphertext: Buffer;
    keyId: string;
}>;
/**
 * Decrypt data using AWS KMS
 */
export declare function decryptData(ciphertext: Buffer): Promise<Buffer>;
/**
 * Generate a data encryption key (envelope encryption)
 */
export declare function generateDataKey(): Promise<{
    plaintext: Buffer;
    ciphertext: Buffer;
}>;
/**
 * Upload encrypted file to S3 using envelope encryption
 */
export declare function uploadEncryptedToS3(bucket: string, key: string, data: Buffer, metadata?: Record<string, string>): Promise<string>;
/**
 * Download and decrypt file from S3
 */
export declare function downloadDecryptedFromS3(bucket: string, key: string): Promise<Buffer>;
/**
 * Get presigned URL for temporary access
 */
export declare function getPresignedUrl(bucket: string, key: string, expiresIn?: number): Promise<string>;
declare const _default: {
    s3Client: any;
    kmsClient: any;
    eksClient: any;
    rdsClient: any;
    cloudTrailClient: any;
    s3Buckets: {
        imaging: string;
        features: string;
        models: string;
        exports: string;
        auditLogs: string;
        backups: string;
    };
    uploadToS3: typeof uploadToS3;
    downloadFromS3: typeof downloadFromS3;
    encryptData: typeof encryptData;
    decryptData: typeof decryptData;
    generateDataKey: typeof generateDataKey;
    uploadEncryptedToS3: typeof uploadEncryptedToS3;
    downloadDecryptedFromS3: typeof downloadDecryptedFromS3;
    getPresignedUrl: typeof getPresignedUrl;
};
export default _default;
//# sourceMappingURL=aws.d.ts.map