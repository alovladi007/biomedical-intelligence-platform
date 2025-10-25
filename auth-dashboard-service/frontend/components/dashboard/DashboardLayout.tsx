'use client';

import { useAuth } from '@/lib/AuthContext';
import { useRouter, usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const navigation = [
    { name: 'Overview', href: '/dashboard', icon: '📊' },
    { name: 'Patients', href: '/dashboard/patients', icon: '👤' },
    { name: 'Predictions', href: '/dashboard/predictions', icon: '🤖' },
    ...(user.role === 'admin' || user.role === 'super_admin' ? [
      { name: 'Users', href: '/dashboard/users', icon: '👥' },
      { name: 'Admin', href: '/dashboard/admin', icon: '⚙️' },
    ] : []),
  ];

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <aside className={`bg-indigo-900 text-white ${sidebarOpen ? 'w-64' : 'w-20'} transition-all duration-300 flex flex-col`}>
        <div className="p-6 flex items-center justify-between">
          {sidebarOpen && <h1 className="text-2xl font-bold">BioMedical AI</h1>}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="text-white hover:bg-indigo-800 p-2 rounded"
          >
            {sidebarOpen ? '◀' : '▶'}
          </button>
        </div>

        <nav className="mt-6 flex-1">
          {navigation.map((item) => (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center px-6 py-3 hover:bg-indigo-800 ${
                pathname === item.href ? 'bg-indigo-800 border-l-4 border-white' : ''
              }`}
            >
              <span className="text-xl">{item.icon}</span>
              {sidebarOpen && <span className="ml-3">{item.name}</span>}
            </Link>
          ))}
        </nav>

        <div className="p-6 border-t border-indigo-800">
          <div className="flex items-center mb-4">
            <div className="w-10 h-10 rounded-full bg-indigo-700 flex items-center justify-center flex-shrink-0">
              {user.first_name?.[0]}{user.last_name?.[0]}
            </div>
            {sidebarOpen && (
              <div className="ml-3 min-w-0">
                <p className="text-sm font-medium truncate">{user.first_name} {user.last_name}</p>
                <p className="text-xs text-indigo-300 truncate">{user.role}</p>
              </div>
            )}
          </div>
          <button
            onClick={logout}
            className="w-full bg-indigo-800 py-2 rounded-lg hover:bg-indigo-700 text-sm"
          >
            {sidebarOpen ? 'Sign Out' : '↪'}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto">
        {children}
      </main>
    </div>
  );
}
