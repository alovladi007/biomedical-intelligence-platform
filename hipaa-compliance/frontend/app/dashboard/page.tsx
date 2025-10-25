'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Shield, AlertTriangle, Activity, Lock, Home, FileText, Settings, Search, CheckCircle, XCircle, Clock, Eye } from 'lucide-react'

interface AuditLog {
  id: string
  userId: string
  userName: string
  action: string
  resourceType: string
  resourceId: string
  ipAddress: string
  timestamp: string
  status: string
  details: string
}

interface SecurityMetric {
  name: string
  value: number
  status: string
  change: string
}

interface Breach {
  id: string
  type: string
  severity: string
  detectedAt: string
  affectedRecords: number
  status: string
  description: string
}

export default function Dashboard() {
  const [auditLogs, setAuditLogs] = useState<AuditLog[]>([])
  const [metrics, setMetrics] = useState<SecurityMetric[]>([])
  const [breaches, setBreaches] = useState<Breach[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedLog, setSelectedLog] = useState<AuditLog | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'audits' | 'breaches'>('audits')

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:5004/api/v1/audits').then(res => res.json()),
      fetch('http://localhost:5004/api/v1/metrics').then(res => res.json()),
      fetch('http://localhost:5004/api/v1/breaches').then(res => res.json())
    ])
      .then(([auditsData, metricsData, breachesData]) => {
        setAuditLogs(auditsData.audits || [])
        setMetrics(metricsData.metrics || [])
        setBreaches(breachesData.breaches || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setLoading(false)
      })
  }, [])

  const filteredLogs = auditLogs.filter(log =>
    log.userName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.action?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    log.resourceType?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'success': return <div className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-600" /><span className="text-green-600">Success</span></div>
      case 'failed': return <div className="flex items-center gap-1"><XCircle className="h-4 w-4 text-red-600" /><span className="text-red-600">Failed</span></div>
      case 'pending': return <div className="flex items-center gap-1"><Clock className="h-4 w-4 text-yellow-600" /><span className="text-yellow-600">Pending</span></div>
      default: return <span className="text-gray-600">Unknown</span>
    }
  }

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getActionColor = (action: string) => {
    if (action.includes('delete') || action.includes('remove')) return 'bg-red-100 text-red-800'
    if (action.includes('update') || action.includes('modify')) return 'bg-yellow-100 text-yellow-800'
    if (action.includes('create') || action.includes('add')) return 'bg-green-100 text-green-800'
    return 'bg-blue-100 text-blue-800'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-purple-600 p-2 rounded-lg">
              <Shield className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">HIPAA Compliance</div>
              <div className="text-xs text-gray-500">Security Hub</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('audits')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'audits'
                  ? 'bg-purple-50 text-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FileText className="h-5 w-5" />
              Audit Logs
            </button>
            <button
              onClick={() => setActiveTab('breaches')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'breaches'
                  ? 'bg-purple-50 text-purple-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <AlertTriangle className="h-5 w-5" />
              Breaches
              {breaches.filter(b => b.status === 'active').length > 0 && (
                <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {breaches.filter(b => b.status === 'active').length}
                </span>
              )}
            </button>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Activity className="h-5 w-5" />
              Metrics
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Lock className="h-5 w-5" />
              Security
            </a>
          </div>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
            <Settings className="h-5 w-5" />
            Settings
          </a>
          <Link href="/" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
            <Home className="h-5 w-5" />
            Home
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">HIPAA Compliance Dashboard</h1>
              <p className="text-sm text-gray-500">Monitor security, audits, and compliance status</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
                Generate Report
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Audit Logs</div>
                <FileText className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{auditLogs.length}</div>
              <div className="text-xs text-blue-600 mt-1">Last 24 hours</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Compliance Score</div>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">98.5%</div>
              <div className="text-xs text-green-600 mt-1">+2.1% this month</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Breaches</div>
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {breaches.filter(b => b.status === 'active').length}
              </div>
              <div className="text-xs text-red-600 mt-1">Requires action</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Access Attempts</div>
                <Lock className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {auditLogs.filter(a => a.action.includes('access')).length}
              </div>
              <div className="text-xs text-blue-600 mt-1">Today</div>
            </div>
          </div>

          {/* Content */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder={`Search ${activeTab}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500"
                />
              </div>
            </div>

            {/* Audit Logs Tab */}
            {activeTab === 'audits' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading audit logs...</div>
                ) : filteredLogs.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No audit logs found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Resource</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">IP Address</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Timestamp</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredLogs.map((log) => (
                        <tr key={log.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedLog(log)}>
                          <td className="px-6 py-4">
                            <div>
                              <div className="font-medium text-gray-900">{log.userName}</div>
                              <div className="text-sm text-gray-500">{log.userId}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getActionColor(log.action)}`}>
                              {log.action}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{log.resourceType}</div>
                              <div className="text-sm text-gray-500">{log.resourceId}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">{log.ipAddress}</td>
                          <td className="px-6 py-4 text-sm text-gray-500">{log.timestamp}</td>
                          <td className="px-6 py-4 text-sm">
                            {getStatusBadge(log.status)}
                          </td>
                          <td className="px-6 py-4">
                            <button className="text-purple-600 hover:text-purple-800 text-sm font-medium flex items-center gap-1">
                              <Eye className="h-4 w-4" />
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {/* Breaches Tab */}
            {activeTab === 'breaches' && (
              <div className="p-6">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading breaches...</div>
                ) : breaches.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No breaches detected</div>
                ) : (
                  <div className="space-y-3">
                    {breaches.map((breach) => (
                      <div key={breach.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <AlertTriangle className="h-5 w-5 text-red-600" />
                              <span className="font-semibold text-gray-900">{breach.type}</span>
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getSeverityColor(breach.severity)}`}>
                                {breach.severity}
                              </span>
                              <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                                breach.status === 'active' ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800'
                              }`}>
                                {breach.status}
                              </span>
                            </div>
                            <div className="text-sm text-gray-700 mb-2">{breach.description}</div>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">Detected:</span>
                                <span className="ml-2 font-medium text-gray-900">{breach.detectedAt}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Affected Records:</span>
                                <span className="ml-2 font-medium text-gray-900">{breach.affectedRecords}</span>
                              </div>
                            </div>
                          </div>
                          <button className="ml-4 px-3 py-1 text-sm bg-purple-600 text-white hover:bg-purple-700 rounded-lg font-medium">
                            Investigate
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Audit Detail Modal */}
      {selectedLog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedLog(null)}>
          <div className="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Audit Log Details</h2>
              <button onClick={() => setSelectedLog(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">User Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedLog.userName}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">User ID</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedLog.userId}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Action</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getActionColor(selectedLog.action)}`}>
                    {selectedLog.action}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Status</div>
                  <div className="mt-1">{getStatusBadge(selectedLog.status)}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Resource Type</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedLog.resourceType}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Resource ID</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedLog.resourceId}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">IP Address</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedLog.ipAddress}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Timestamp</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedLog.timestamp}</div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-2">Details</div>
                <div className="p-4 bg-gray-50 rounded-lg text-sm text-gray-700">
                  {selectedLog.details}
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
                  Export Log
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  Flag for Review
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function X({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  )
}
