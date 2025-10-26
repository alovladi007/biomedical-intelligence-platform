'use client';

import Link from 'next/link';

export default function DashboardPage() {
  // Get current time greeting
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  return (
    <div>
      {/* Welcome Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white p-8 rounded-lg shadow-lg mb-8">
        <h1 className="text-3xl font-bold mb-2">
          {getGreeting()}!
        </h1>
        <p className="text-blue-100">
          Welcome to the Biomedical Intelligence Platform
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 mb-1">Total Patients</div>
          <div className="text-3xl font-bold text-blue-600">0</div>
          <div className="text-xs text-gray-400 mt-1">No patients yet</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 mb-1">AI Predictions</div>
          <div className="text-3xl font-bold text-green-600">0</div>
          <div className="text-xs text-gray-400 mt-1">No predictions yet</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 mb-1">Active Users</div>
          <div className="text-3xl font-bold text-purple-600">1</div>
          <div className="text-xs text-gray-400 mt-1">You are logged in</div>
        </div>
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="text-sm text-gray-500 mb-1">System Status</div>
          <div className="text-2xl font-bold text-green-600">✓ Healthy</div>
          <div className="text-xs text-gray-400 mt-1">All systems operational</div>
        </div>
      </div>

      {/* Main Navigation Cards */}
      <h2 className="text-2xl font-bold mb-4">Quick Access</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Link href="/dashboard/patients" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="text-4xl mb-4">👤</div>
          <h2 className="text-xl font-semibold mb-2">Patients</h2>
          <p className="text-gray-600">Manage patient records</p>
        </Link>

        <Link href="/dashboard/predictions" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="text-4xl mb-4">🤖</div>
          <h2 className="text-xl font-semibold mb-2">AI Predictions</h2>
          <p className="text-gray-600">View prediction history</p>
        </Link>

        <a
          href="http://localhost:3007"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow"
        >
          <div className="text-4xl mb-4">🩺</div>
          <h2 className="text-xl font-semibold mb-2">AI Diagnostics</h2>
          <p className="text-gray-600">Symptom checker & lab analysis</p>
        </a>

        <Link href="/dashboard/users" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="text-4xl mb-4">👥</div>
          <h2 className="text-xl font-semibold mb-2">Users</h2>
          <p className="text-gray-600">Manage user accounts</p>
        </Link>

        <Link href="/dashboard/admin" className="bg-white p-6 rounded-lg shadow hover:shadow-lg transition-shadow">
          <div className="text-4xl mb-4">⚙️</div>
          <h2 className="text-xl font-semibold mb-2">Admin Panel</h2>
          <p className="text-gray-600">System administration</p>
        </Link>
      </div>
    </div>
  );
}
