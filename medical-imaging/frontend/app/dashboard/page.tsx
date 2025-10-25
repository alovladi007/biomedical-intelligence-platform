'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Scan, Activity, TrendingUp, Image, Home, FileText, Settings, Search, CheckCircle, Clock, AlertCircle, Eye } from 'lucide-react'

interface Study {
  id: string
  patientId: string
  patientName: string
  studyType: string
  modality: string
  studyDate: string
  status: string
  aiAnalysis: {
    completed: boolean
    findings: string[]
    confidence: number
  }
  imageCount: number
  radiologist: string
}

export default function Dashboard() {
  const [studies, setStudies] = useState<Study[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedStudy, setSelectedStudy] = useState<Study | null>(null)
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetch('http://localhost:5002/api/v1/studies')
      .then(res => res.json())
      .then(data => {
        setStudies(data.studies || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching studies:', err)
        setLoading(false)
      })
  }, [])

  const filteredStudies = studies.filter(s =>
    s.patientName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.studyType?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.modality?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusIcon = (status: string) => {
    switch(status) {
      case 'completed': return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'processing': return <Clock className="h-5 w-5 text-yellow-600" />
      case 'pending': return <AlertCircle className="h-5 w-5 text-blue-600" />
      default: return <AlertCircle className="h-5 w-5 text-gray-600" />
    }
  }

  const getModalityColor = (modality: string) => {
    switch(modality) {
      case 'CT': return 'bg-blue-100 text-blue-800'
      case 'MRI': return 'bg-purple-100 text-purple-800'
      case 'X-Ray': return 'bg-gray-100 text-gray-800'
      case 'Ultrasound': return 'bg-teal-100 text-teal-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Scan className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">Medical Imaging</div>
              <div className="text-xs text-gray-500">AI Analysis</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <a href="#" className="flex items-center gap-3 px-4 py-3 bg-indigo-50 text-indigo-600 rounded-lg font-medium">
              <Activity className="h-5 w-5" />
              Studies
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Image className="h-5 w-5" />
              DICOM Viewer
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
              <h1 className="text-2xl font-bold text-gray-900">Medical Imaging Dashboard</h1>
              <p className="text-sm text-gray-500">DICOM studies and AI-powered analysis</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">
                Upload Study
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Total Studies</div>
                <Activity className="h-5 w-5 text-indigo-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{studies.length}</div>
              <div className="text-xs text-green-600 mt-1">+15% from last week</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">AI Analyzed</div>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {studies.filter(s => s.aiAnalysis?.completed).length}
              </div>
              <div className="text-xs text-green-600 mt-1">Analysis complete</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Processing</div>
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {studies.filter(s => s.status === 'processing').length}
              </div>
              <div className="text-xs text-yellow-600 mt-1">In progress</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Avg Confidence</div>
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {studies.filter(s => s.aiAnalysis?.completed).length > 0
                  ? `${((studies.filter(s => s.aiAnalysis?.completed).reduce((acc, s) => acc + (s.aiAnalysis?.confidence || 0), 0) / studies.filter(s => s.aiAnalysis?.completed).length) * 100).toFixed(1)}%`
                  : '0%'
                }
              </div>
              <div className="text-xs text-blue-600 mt-1">AI accuracy</div>
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
                    placeholder="Search studies by patient, type, or modality..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
                <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  Filters
                </button>
              </div>
            </div>

            {/* Studies Table */}
            <div className="overflow-x-auto">
              {loading ? (
                <div className="p-12 text-center text-gray-500">
                  Loading studies...
                </div>
              ) : filteredStudies.length === 0 ? (
                <div className="p-12 text-center text-gray-500">
                  No studies found
                </div>
              ) : (
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Study Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Modality</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Images</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">AI Analysis</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {filteredStudies.map((study) => (
                      <tr key={study.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedStudy(study)}>
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-medium text-gray-900">{study.patientName}</div>
                            <div className="text-sm text-gray-500">{study.patientId}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{study.studyType}</td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getModalityColor(study.modality)}`}>
                            {study.modality}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{study.imageCount}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{study.studyDate}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            {getStatusIcon(study.status)}
                            <span className="text-sm capitalize">{study.status}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          {study.aiAnalysis?.completed ? (
                            <div className="flex items-center gap-2">
                              <CheckCircle className="h-4 w-4 text-green-600" />
                              <span className="text-sm text-green-600">{((study.aiAnalysis?.confidence || 0) * 100).toFixed(0)}%</span>
                            </div>
                          ) : (
                            <span className="text-sm text-gray-400">Pending</span>
                          )}
                        </td>
                        <td className="px-6 py-4">
                          <button className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center gap-1">
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
          </div>
        </div>
      </div>

      {/* Detail Modal */}
      {selectedStudy && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedStudy(null)}>
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Study Details</h2>
              <button onClick={() => setSelectedStudy(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedStudy.patientName}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient ID</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedStudy.patientId}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Study Type</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedStudy.studyType}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Modality</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getModalityColor(selectedStudy.modality)}`}>
                    {selectedStudy.modality}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Study Date</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedStudy.studyDate}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Image Count</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedStudy.imageCount} images</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Radiologist</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedStudy.radiologist}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Status</div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(selectedStudy.status)}
                    <span className="text-lg font-semibold text-gray-900 capitalize">{selectedStudy.status}</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-3">AI Analysis Results</div>
                {selectedStudy.aiAnalysis?.completed ? (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                      <span className="text-sm font-medium text-green-900">Analysis Complete</span>
                      <span className="text-sm text-green-700">Confidence: {((selectedStudy.aiAnalysis?.confidence || 0) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="text-sm font-medium text-gray-700 mb-2">Findings:</div>
                    <ul className="space-y-2">
                      {selectedStudy.aiAnalysis?.findings?.map((finding, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                          <span className="text-indigo-600 mt-1">•</span>
                          <span>{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : (
                  <div className="p-4 bg-yellow-50 rounded-lg text-center text-sm text-yellow-800">
                    AI analysis pending or in progress
                  </div>
                )}
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium">
                  Open DICOM Viewer
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  Generate Report
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
