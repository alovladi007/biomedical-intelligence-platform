'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();
  const [showOptions, setShowOptions] = useState(false);

  useEffect(() => {
    // Show options after a brief delay
    const timer = setTimeout(() => {
      const token = localStorage.getItem('access_token');
      if (token) {
        router.push('/dashboard');
      } else {
        setShowOptions(true);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [router]);

  const handleSkipLogin = () => {
    // Set a temporary bypass token
    localStorage.setItem('bypass_auth', 'true');
    router.push('/dashboard');
  };

  const handleLogin = () => {
    router.push('/login');
  };

  if (!showOptions) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="bg-white p-8 rounded-lg shadow-xl max-w-md w-full">
        <h1 className="text-3xl font-bold text-center mb-2 text-gray-800">
          Biomedical Intelligence Platform
        </h1>
        <p className="text-center text-gray-600 mb-8">
          Choose how to proceed
        </p>

        <div className="space-y-4">
          <button
            onClick={handleLogin}
            className="w-full bg-indigo-600 text-white py-3 px-4 rounded-lg hover:bg-indigo-700 transition-colors font-medium"
          >
            Login with Account
          </button>

          <button
            onClick={handleSkipLogin}
            className="w-full bg-gray-200 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-300 transition-colors font-medium"
          >
            Skip Login (Demo Mode)
          </button>
        </div>

        <p className="text-xs text-gray-500 text-center mt-6">
          Skip login is for demonstration purposes only
        </p>
      </div>
    </div>
  );
}
