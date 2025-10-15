/**
 * Global type declarations for third-party modules without TypeScript definitions
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
  }

  export class device extends EventEmitter {
    constructor(options: DeviceOptions);
    subscribe(topic: string | string[], options?: any, callback?: (error?: Error) => void): void;
    unsubscribe(topic: string | string[], callback?: (error?: Error) => void): void;
    publish(topic: string, message: string | Buffer, options?: any, callback?: (error?: Error) => void): void;
    end(force?: boolean, callback?: () => void): void;
    on(event: 'connect', listener: (connack: any) => void): this;
    on(event: 'reconnect', listener: () => void): this;
    on(event: 'close', listener: () => void): this;
    on(event: 'offline', listener: () => void): this;
    on(event: 'error', listener: (error: Error) => void): this;
    on(event: 'message', listener: (topic: string, payload: Buffer) => void): this;
    on(event: string, listener: (...args: any[]) => void): this;
  }
}
