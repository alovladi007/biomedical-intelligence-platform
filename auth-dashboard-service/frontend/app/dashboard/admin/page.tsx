'use client';

import { useState, useEffect } from 'react';
import { adminAPI } from '@/lib/api';

export default function AdminPage() {
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [logsRes, healthRes] = await Promise.all([
        adminAPI.auditLogs({ limit: 10 }),
        adminAPI.systemHealth(),
      ]);
      setAuditLogs(logsRes.data);
      setSystemHealth(healthRes.data);
    } catch (err) {
      console.error('Failed to load admin data', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Admin Panel</h1>

      {/* System Health */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Database</h3>
          <p className="text-2xl font-bold text-green-600">
            {systemHealth?.database?.status || 'Loading...'}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Connections</h3>
          <p className="text-2xl font-bold">
            {systemHealth?.database?.pool_size || '0'} / {systemHealth?.database?.checked_in_connections || '0'}
          </p>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Status</h3>
          <p className="text-2xl font-bold text-green-600">Healthy</p>
        </div>
      </div>

      {/* Recent Audit Logs */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-bold mb-4">Recent Audit Logs</h2>
        {loading ? (
          <div className="text-center py-12">Loading...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Time</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">User</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Action</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Resource</th>
                  <th className="px-4 py-2 text-left text-xs font-medium text-gray-500">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {auditLogs.map((log: any) => (
                  <tr key={log.id} className="hover:bg-gray-50">
                    <td className="px-4 py-2 text-sm">{new Date(log.created_at).toLocaleString()}</td>
                    <td className="px-4 py-2 text-sm">{log.username || 'System'}</td>
                    <td className="px-4 py-2 text-sm">{log.action}</td>
                    <td className="px-4 py-2 text-sm">{log.resource_type}</td>
                    <td className="px-4 py-2 text-sm">
                      <span className={`px-2 py-1 text-xs rounded ${
                        log.status_code < 400 ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {log.status_code}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
