/**
 * Type definitions for aws-iot-device-sdk
 * This is a minimal type declaration to enable TypeScript compilation
 */

declare module 'aws-iot-device-sdk' {
  import { EventEmitter } from 'events';

  export interface DeviceOptions {
    keyPath?: string;
    certPath?: string;
    caPath?: string;
    clientId: string;
    host?: string;
    port?: number;
    region?: string;
    protocol?: 'mqtts' | 'wss' | 'wss-custom-auth' | 'mqtt';
    keepalive?: number;
    connectTimeout?: number;
    reconnectPeriod?: number;
    fastDisconnectDetection?: boolean;
    baseReconnectTimeMs?: number;
    maximumReconnectTimeMs?: number;
    minimumConnectionTimeMs?: number;
    autoResubscribe?: boolean;
    offlineQueueing?: boolean;
    offlineQueueMaxSize?: number;
    offlineQueueDropBehavior?: 'oldest' | 'newest';
    will?: {
      topic: string;
      payload: string;
      qos?: 0 | 1 | 2;
      retain?: boolean;
    };
  }

  export class device extends EventEmitter {
    constructor(options: DeviceOptions);

    /**
     * Connect to AWS IoT
     */
    connect(): void;

    /**
     * Subscribe to an MQTT topic
     */
    subscribe(topic: string | string[], options?: any, callback?: (error?: Error) => void): void;

    /**
     * Unsubscribe from an MQTT topic
     */
    unsubscribe(topic: string | string[], callback?: (error?: Error) => void): void;

    /**
     * Publish to an MQTT topic
     */
    publish(topic: string, message: string | Buffer, options?: any, callback?: (error?: Error) => void): void;

    /**
     * End the connection
     */
    end(force?: boolean, callback?: () => void): void;

    /**
     * Update credentials
     */
    updateWebSocketCredentials(
      accessKeyId: string,
      secretKey: string,
      sessionToken: string,
      expiration?: Date
    ): void;

    // Event handlers
    on(event: 'connect', listener: (connack: any) => void): this;
    on(event: 'reconnect', listener: () => void): this;
    on(event: 'close', listener: () => void): this;
    on(event: 'offline', listener: () => void): this;
    on(event: 'error', listener: (error: Error) => void): this;
    on(event: 'message', listener: (topic: string, payload: Buffer) => void): this;
    on(event: 'packetsend', listener: (packet: any) => void): this;
    on(event: 'packetreceive', listener: (packet: any) => void): this;
    on(event: string, listener: (...args: any[]) => void): this;
  }

  export interface ThingShadowOptions extends DeviceOptions {
    operationTimeout?: number;
  }

  export class thingShadow extends device {
    constructor(options: ThingShadowOptions);

    /**
     * Register interest in a thing shadow
     */
    register(
      thingName: string,
      options?: any,
      callback?: (error?: Error, failedTopics?: string[]) => void
    ): void;

    /**
     * Unregister interest in a thing shadow
     */
    unregister(thingName: string): void;

    /**
     * Update a thing shadow
     */
    update(
      thingName: string,
      stateObject: any,
      clientToken?: string
    ): string | null;

    /**
     * Get a thing shadow
     */
    get(thingName: string, clientToken?: string): string | null;

    /**
     * Delete a thing shadow
     */
    delete(thingName: string, clientToken?: string): string | null;

    /**
     * Publish to a thing shadow
     */
    publish(
      topic: string,
      message: string | Buffer,
      options?: any,
      callback?: (error?: Error) => void
    ): void;

    // Shadow-specific events
    on(event: 'status', listener: (thingName: string, stat: string, clientToken: string, stateObject: any) => void): this;
    on(event: 'delta', listener: (thingName: string, stateObject: any) => void): this;
    on(event: 'timeout', listener: (thingName: string, clientToken: string) => void): this;
    on(event: 'foreignStateChange', listener: (thingName: string, operation: string, stateObject: any) => void): this;
  }

  export interface JobsOptions extends DeviceOptions {
    operationTimeout?: number;
  }

  export class jobs extends device {
    constructor(options: JobsOptions);

    /**
     * Subscribe to job execution events for a thing
     */
    subscribeToJobs(
      thingName: string,
      operationName: string,
      callback?: (error?: Error) => void
    ): void;

    /**
     * Start the next pending job execution
     */
    startNextPendingJobExecution(
      thingName: string,
      statusDetails?: any,
      clientToken?: string
    ): string | null;

    /**
     * Describe a job execution
     */
    describeJobExecution(
      thingName: string,
      jobId: string,
      options?: any,
      clientToken?: string
    ): string | null;

    /**
     * Update a job execution
     */
    updateJobExecution(
      thingName: string,
      jobId: string,
      status: 'QUEUED' | 'IN_PROGRESS' | 'SUCCEEDED' | 'FAILED' | 'REJECTED' | 'REMOVED' | 'CANCELED',
      statusDetails?: any,
      options?: any,
      clientToken?: string
    ): string | null;
  }
}
