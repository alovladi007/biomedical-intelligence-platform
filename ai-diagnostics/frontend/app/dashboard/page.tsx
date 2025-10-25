'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Brain, Activity, TrendingUp, Users, Home, FileText, Settings, LogOut, AlertCircle, CheckCircle, Clock, Search } from 'lucide-react'

interface Diagnostic {
  id: string
  patientId: string
  patientName: string
  condition: string
  riskScore: number
  confidence: number
  date: string
  status: string
}

export default function Dashboard() {
  const [diagnostics, setDiagnostics] = useState<Diagnostic[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDiagnostic, setSelectedDiagnostic] = useState<Diagnostic | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetch('http://localhost:5001/api/v1/diagnostics')
      .then(res => res.json())
      .then(data => {
        setDiagnostics(data.diagnostics || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching diagnostics:', err)
        setLoading(false)
      })
  }, [])

  const filteredDiagnostics = diagnostics.filter(d =>
    d.patientName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.condition?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'text-red-600 bg-red-50'
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'pending-review': return <Clock className="h-5 w-5 text-yellow-600" />
      default: return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <Brain className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">AI Diagnostics</div>
              <div className="text-xs text-gray-500">Dashboard</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <a href="#" className="flex items-center gap-3 px-4 py-3 bg-blue-50 text-blue-600 rounded-lg font-medium">
              <Activity className="h-5 w-5" />
              Diagnostics
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Users className="h-5 w-5" />
              Patients
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <TrendingUp className="h-5 w-5" />
              Analytics
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <FileText className="h-5 w-5" />
              Reports
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
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">AI Diagnostics Dashboard</h1>
              <p className="text-sm text-gray-500">Manage and review diagnostic predictions</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                New Diagnostic
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Total Cases</div>
                <Activity className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{diagnostics.length}</div>
              <div className="text-xs text-green-600 mt-1">+12% from last month</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">High Risk</div>
                <AlertCircle className="h-5 w-5 text-red-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {diagnostics.filter(d => d.riskScore >= 0.7).length}
              </div>
              <div className="text-xs text-red-600 mt-1">Requires attention</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Avg Confidence</div>
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {diagnostics.length > 0
                  ? `${((diagnostics.reduce((acc, d) => acc + d.confidence, 0) / diagnostics.length) * 100).toFixed(1)}%`
                  : '0%'
                }
              </div>
              <div className="text-xs text-green-600 mt-1">Above threshold</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Pending Review</div>
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {diagnostics.filter(d => d.status === 'pending-review').length}
              </div>
              <div className="text-xs text-yellow-600 mt-1">Needs review</div>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="bg-white rounded-lg border border-gray-200 mb-6">
            <div className="p-4 border-b border-gray-200">
              <div className="flex items-center gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search patients or conditions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  Filters
                </button>
              </div>
            </div>

            {/* Diagnostics Table */}
            <div className="overflow-x-auto">
              {loading ? (
                <div className="p-12 text-center text-gray-500">
                  Loading diagnostics...
                </div>
              ) : filteredDiagnostics.length === 0 ? (
                <div className="p-12 text-center text-gray-500">
                  No diagnostics found
                </div>
              ) : (
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Condition</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Confidence</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredDiagnostics.map((diagnostic) => (
                      <tr key={diagnostic.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedDiagnostic(diagnostic)}>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{diagnostic.patientName}</div>
                            <div className="text-sm text-gray-500">{diagnostic.patientId}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{diagnostic.condition}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(diagnostic.riskScore)}`}>
                            {(diagnostic.riskScore * 100).toFixed(0)}%
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{(diagnostic.confidence * 100).toFixed(1)}%</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{diagnostic.date}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(diagnostic.status)}
                            <span className="text-sm capitalize">{diagnostic.status.replace('-', ' ')}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedDiagnostic && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedDiagnostic(null)}>
          <div className="bg-white rounded-lg max-w-2xl w-full p-6" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Diagnostic Details</h2>
              <button onClick={() => setSelectedDiagnostic(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDiagnostic.patientName}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient ID</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDiagnostic.patientId}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Condition</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDiagnostic.condition}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Date</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDiagnostic.date}</div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Risk Score</div>
                    <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(selectedDiagnostic.riskScore)}`}>
                      {(selectedDiagnostic.riskScore * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Model Confidence</div>
                    <div className="text-lg font-semibold text-gray-900">{(selectedDiagnostic.confidence * 100).toFixed(1)}%</div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium">
                  Approve Diagnosis
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  Request Review
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
