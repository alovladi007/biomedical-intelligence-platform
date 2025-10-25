'use client';

import { useAuth } from '@/lib/AuthContext';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard Overview</h1>

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

        {(user?.role === 'admin' || user?.role === 'super_admin') && (
          <>
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
          </>
        )}
      </div>
    </div>
  );
}
