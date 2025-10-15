"use strict";
/**
 * AWS Services Configuration
 * Handles S3, KMS, EKS, RDS, CloudTrail, and other AWS services
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.kmsKeyId = exports.s3Buckets = exports.cloudTrailClient = exports.rdsClient = exports.eksClient = exports.kmsClient = exports.s3Client = exports.awsConfig = void 0;
exports.uploadToS3 = uploadToS3;
exports.downloadFromS3 = downloadFromS3;
exports.encryptData = encryptData;
exports.decryptData = decryptData;
exports.generateDataKey = generateDataKey;
exports.uploadEncryptedToS3 = uploadEncryptedToS3;
exports.downloadDecryptedFromS3 = downloadDecryptedFromS3;
exports.getPresignedUrl = getPresignedUrl;
const client_s3_1 = require("@aws-sdk/client-s3");
const client_kms_1 = require("@aws-sdk/client-kms");
const client_eks_1 = require("@aws-sdk/client-eks");
const client_rds_1 = require("@aws-sdk/client-rds");
const client_cloudtrail_1 = require("@aws-sdk/client-cloudtrail");
const dotenv_1 = require("dotenv");
(0, dotenv_1.config)();
// AWS Configuration
exports.awsConfig = {
    region: process.env.AWS_REGION || 'us-east-1',
    credentials: {
        accessKeyId: process.env.AWS_ACCESS_KEY_ID || '',
        secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY || '',
    },
};
// S3 Client
exports.s3Client = new client_s3_1.S3Client(exports.awsConfig);
// KMS Client for encryption
exports.kmsClient = new client_kms_1.KMSClient(exports.awsConfig);
// EKS Client
exports.eksClient = new client_eks_1.EKSClient(exports.awsConfig);
// RDS Client
exports.rdsClient = new client_rds_1.RDSClient(exports.awsConfig);
// CloudTrail Client
exports.cloudTrailClient = new client_cloudtrail_1.CloudTrailClient(exports.awsConfig);
// S3 Bucket Configuration
exports.s3Buckets = {
    imaging: process.env.S3_BUCKET_IMAGING || 'biomedical-imaging-data',
    features: process.env.S3_BUCKET_FEATURES || 'biomedical-features',
    models: process.env.S3_BUCKET_MODELS || 'biomedical-models',
    exports: process.env.S3_BUCKET_EXPORTS || 'biomedical-exports',
    auditLogs: process.env.HIPAA_AUDIT_LOG_BUCKET || 'biomedical-audit-logs',
    backups: process.env.HIPAA_BACKUP_BUCKET || 'biomedical-backups',
};
// KMS Key Configuration
exports.kmsKeyId = process.env.AWS_KMS_KEY_ID || '';
/**
 * Upload file to S3 with server-side encryption using KMS
 */
async function uploadToS3(bucket, key, data, metadata) {
    try {
        const command = new client_s3_1.PutObjectCommand({
            Bucket: bucket,
            Key: key,
            Body: data,
            ServerSideEncryption: 'aws:kms',
            SSEKMSKeyId: exports.kmsKeyId,
            Metadata: metadata,
        });
        await exports.s3Client.send(command);
        return `s3://${bucket}/${key}`;
    }
    catch (error) {
        console.error('Error uploading to S3:', error);
        throw error;
    }
}
/**
 * Download file from S3
 */
async function downloadFromS3(bucket, key) {
    try {
        const command = new client_s3_1.GetObjectCommand({
            Bucket: bucket,
            Key: key,
        });
        const response = await exports.s3Client.send(command);
        const stream = response.Body;
        return new Promise((resolve, reject) => {
            const chunks = [];
            stream.on('data', (chunk) => chunks.push(chunk));
            stream.on('error', reject);
            stream.on('end', () => resolve(Buffer.concat(chunks)));
        });
    }
    catch (error) {
        console.error('Error downloading from S3:', error);
        throw error;
    }
}
/**
 * Encrypt data using AWS KMS
 */
async function encryptData(plaintext) {
    try {
        const command = new client_kms_1.EncryptCommand({
            KeyId: exports.kmsKeyId,
            Plaintext: Buffer.isBuffer(plaintext) ? plaintext : Buffer.from(plaintext),
        });
        const response = await exports.kmsClient.send(command);
        return {
            ciphertext: Buffer.from(response.CiphertextBlob),
            keyId: response.KeyId || exports.kmsKeyId,
        };
    }
    catch (error) {
        console.error('Error encrypting data with KMS:', error);
        throw error;
    }
}
/**
 * Decrypt data using AWS KMS
 */
async function decryptData(ciphertext) {
    try {
        const command = new client_kms_1.DecryptCommand({
            CiphertextBlob: ciphertext,
        });
        const response = await exports.kmsClient.send(command);
        return Buffer.from(response.Plaintext);
    }
    catch (error) {
        console.error('Error decrypting data with KMS:', error);
        throw error;
    }
}
/**
 * Generate a data encryption key (envelope encryption)
 */
async function generateDataKey() {
    try {
        const command = new client_kms_1.GenerateDataKeyCommand({
            KeyId: exports.kmsKeyId,
            KeySpec: 'AES_256',
        });
        const response = await exports.kmsClient.send(command);
        return {
            plaintext: Buffer.from(response.Plaintext),
            ciphertext: Buffer.from(response.CiphertextBlob),
        };
    }
    catch (error) {
        console.error('Error generating data key:', error);
        throw error;
    }
}
/**
 * Upload encrypted file to S3 using envelope encryption
 */
async function uploadEncryptedToS3(bucket, key, data, metadata) {
    try {
        // Generate data encryption key
        const { plaintext: dataKey, ciphertext: encryptedDataKey } = await generateDataKey();
        // Encrypt data with data key (using AES-256-GCM)
        const crypto = require('crypto');
        const iv = crypto.randomBytes(16);
        const cipher = crypto.createCipheriv('aes-256-gcm', dataKey, iv);
        const encryptedData = Buffer.concat([
            cipher.update(data),
            cipher.final(),
        ]);
        const authTag = cipher.getAuthTag();
        // Combine encrypted data key, IV, auth tag, and encrypted data
        const combinedData = Buffer.concat([
            Buffer.from([encryptedDataKey.length]),
            encryptedDataKey,
            iv,
            authTag,
            encryptedData,
        ]);
        // Upload to S3
        return await uploadToS3(bucket, key, combinedData, metadata);
    }
    catch (error) {
        console.error('Error uploading encrypted file to S3:', error);
        throw error;
    }
}
/**
 * Download and decrypt file from S3
 */
async function downloadDecryptedFromS3(bucket, key) {
    try {
        // Download encrypted file
        const combinedData = await downloadFromS3(bucket, key);
        // Extract components
        const encryptedDataKeyLength = combinedData[0];
        let offset = 1;
        const encryptedDataKey = combinedData.slice(offset, offset + encryptedDataKeyLength);
        offset += encryptedDataKeyLength;
        const iv = combinedData.slice(offset, offset + 16);
        offset += 16;
        const authTag = combinedData.slice(offset, offset + 16);
        offset += 16;
        const encryptedData = combinedData.slice(offset);
        // Decrypt data key using KMS
        const dataKey = await decryptData(encryptedDataKey);
        // Decrypt data using data key
        const crypto = require('crypto');
        const decipher = crypto.createDecipheriv('aes-256-gcm', dataKey, iv);
        decipher.setAuthTag(authTag);
        const decryptedData = Buffer.concat([
            decipher.update(encryptedData),
            decipher.final(),
        ]);
        return decryptedData;
    }
    catch (error) {
        console.error('Error downloading and decrypting file from S3:', error);
        throw error;
    }
}
/**
 * Get presigned URL for temporary access
 */
async function getPresignedUrl(bucket, key, expiresIn = 3600) {
    const { getSignedUrl } = require('@aws-sdk/s3-request-presigner');
    try {
        const command = new client_s3_1.GetObjectCommand({
            Bucket: bucket,
            Key: key,
        });
        const url = await getSignedUrl(exports.s3Client, command, { expiresIn });
        return url;
    }
    catch (error) {
        console.error('Error generating presigned URL:', error);
        throw error;
    }
}
exports.default = {
    s3Client: exports.s3Client,
    kmsClient: exports.kmsClient,
    eksClient: exports.eksClient,
    rdsClient: exports.rdsClient,
    cloudTrailClient: exports.cloudTrailClient,
    s3Buckets: exports.s3Buckets,
    uploadToS3,
    downloadFromS3,
    encryptData,
    decryptData,
    generateDataKey,
    uploadEncryptedToS3,
    downloadDecryptedFromS3,
    getPresignedUrl,
};
//# sourceMappingURL=aws.js.map