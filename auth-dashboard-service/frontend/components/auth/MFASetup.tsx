'use client';

import { useState, useEffect } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { authAPI } from '@/lib/api';

export default function MFASetup({ onComplete }: { onComplete?: () => void }) {
  const [qrCodeUrl, setQrCodeUrl] = useState('');
  const [secret, setSecret] = useState('');
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [verificationCode, setVerificationCode] = useState('');
  const [step, setStep] = useState<'qr' | 'verify' | 'complete'>('qr');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setupMFA();
  }, []);

  const setupMFA = async () => {
    try {
      const response = await authAPI.setupMFA();
      setQrCodeUrl(response.data.qr_code_url);
      setSecret(response.data.secret);
      setBackupCodes(response.data.backup_codes);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to setup MFA');
    }
  };

  const verifyMFA = async () => {
    setLoading(true);
    setError('');

    try {
      await authAPI.verifyMFA({ mfa_token: verificationCode });
      setStep('complete');
      setTimeout(() => onComplete?.(), 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Invalid verification code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6">
      {step === 'qr' && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Set Up Two-Factor Authentication</h2>
          <p className="mb-6 text-gray-600">
            Scan this QR code with your authenticator app (Google Authenticator, Authy, etc.)
          </p>

          {qrCodeUrl && (
            <div className="bg-white p-6 rounded-lg shadow mb-6 flex justify-center">
              <QRCodeSVG value={qrCodeUrl} size={256} />
            </div>
          )}

          <div className="mb-6 bg-gray-50 p-4 rounded-lg">
            <p className="text-sm font-medium mb-2">Manual Entry Key:</p>
            <p className="font-mono text-sm break-all">{secret}</p>
          </div>

          {backupCodes.length > 0 && (
            <div className="mb-6">
              <h3 className="font-semibold mb-2">Backup Codes</h3>
              <p className="text-sm text-gray-600 mb-4">
                Save these codes in a safe place. You can use them to access your account if you lose your device.
              </p>
              <div className="grid grid-cols-2 gap-2 bg-gray-50 p-4 rounded">
                {backupCodes.map((code, i) => (
                  <div key={i} className="font-mono text-sm">{code}</div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => setStep('verify')}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 font-medium"
          >
            Continue to Verification
          </button>
        </div>
      )}

      {step === 'verify' && (
        <div>
          <h2 className="text-2xl font-bold mb-4">Verify Your Setup</h2>
          <p className="mb-6 text-gray-600">
            Enter the 6-digit code from your authenticator app
          </p>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm">
              {error}
            </div>
          )}

          <input
            type="text"
            value={verificationCode}
            onChange={(e) => setVerificationCode(e.target.value.replace(/\D/g, ''))}
            maxLength={6}
            className="w-full px-4 py-3 border rounded-lg text-center text-2xl tracking-widest mb-6"
            placeholder="000000"
            autoFocus
          />

          <button
            onClick={verifyMFA}
            disabled={loading || verificationCode.length !== 6}
            className="w-full bg-indigo-600 text-white py-3 rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 font-medium"
          >
            {loading ? 'Verifying...' : 'Verify and Enable MFA'}
          </button>
        </div>
      )}

      {step === 'complete' && (
        <div className="text-center">
          <div className="text-green-600 text-6xl mb-4">✓</div>
          <h2 className="text-2xl font-bold mb-2">MFA Enabled Successfully!</h2>
          <p className="text-gray-600">Your account is now protected with two-factor authentication.</p>
        </div>
      )}
    </div>
  );
}
