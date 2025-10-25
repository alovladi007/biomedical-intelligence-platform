'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Dna, Activity, TrendingUp, Users, Home, FileText, Settings, Search, CheckCircle, Clock, AlertCircle, FlaskConical, Database, Eye } from 'lucide-react'

interface GenomicAnalysis {
  id: string
  patientId: string
  patientName: string
  analysisType: string
  status: string
  submittedDate: string
  completedDate: string | null
  variants: number
  clinicalVariants: number
  pathogenicVariants: number
  pharmacogenomics: boolean
  findings: string[]
  riskScore: number
}

interface Variant {
  id: string
  gene: string
  chromosome: string
  position: string
  variantType: string
  pathogenicity: string
  clinicalSignificance: string
  diseases: string[]
}

export default function Dashboard() {
  const [analyses, setAnalyses] = useState<GenomicAnalysis[]>([])
  const [variants, setVariants] = useState<Variant[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedAnalysis, setSelectedAnalysis] = useState<GenomicAnalysis | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'analyses' | 'variants'>('analyses')

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:5007/api/v1/analyses').then(res => res.json()),
      fetch('http://localhost:5007/api/v1/variants').then(res => res.json())
    ])
      .then(([analysesData, variantsData]) => {
        setAnalyses(analysesData.analyses || [])
        setVariants(variantsData.variants || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setLoading(false)
      })
  }, [])

  const filteredAnalyses = analyses.filter(a =>
    a.patientName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    a.analysisType?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'completed': return <div className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-600" /><span className="text-green-600">Completed</span></div>
      case 'processing': return <div className="flex items-center gap-1"><Clock className="h-4 w-4 text-blue-600" /><span className="text-blue-600">Processing</span></div>
      case 'pending': return <div className="flex items-center gap-1"><AlertCircle className="h-4 w-4 text-yellow-600" /><span className="text-yellow-600">Pending</span></div>
      default: return <span className="text-gray-600">Unknown</span>
    }
  }

  const getRiskColor = (score: number) => {
    if (score >= 0.7) return 'text-red-600 bg-red-50'
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  const getPathogenicityColor = (pathogenicity: string) => {
    switch(pathogenicity) {
      case 'Pathogenic': return 'bg-red-100 text-red-800'
      case 'Likely Pathogenic': return 'bg-orange-100 text-orange-800'
      case 'Benign': return 'bg-green-100 text-green-800'
      case 'Likely Benign': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-purple-600 p-2 rounded-lg">
              <Dna className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">Genomic Intelligence</div>
              <div className="text-xs text-gray-500">Precision Medicine</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('analyses')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'analyses' ? 'bg-purple-50 text-purple-600' : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Activity className="h-5 w-5" />
              Genomic Analyses
            </button>
            <button
              onClick={() => setActiveTab('variants')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'variants' ? 'bg-purple-50 text-purple-600' : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Database className="h-5 w-5" />
              Variants
            </button>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <FlaskConical className="h-5 w-5" />
              Pharmacogenomics
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <TrendingUp className="h-5 w-5" />
              Population Studies
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
              <h1 className="text-2xl font-bold text-gray-900">Genomic Intelligence Dashboard</h1>
              <p className="text-sm text-gray-500">Precision medicine and genomic analysis platform</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
                New Analysis
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Total Analyses</div>
                <Activity className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{analyses.length}</div>
              <div className="text-xs text-green-600 mt-1">+12 this week</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Completed</div>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {analyses.filter(a => a.status === 'completed').length}
              </div>
              <div className="text-xs text-green-600 mt-1">Analysis complete</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Pathogenic Variants</div>
                <AlertCircle className="h-5 w-5 text-red-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {analyses.reduce((sum, a) => sum + (a.pathogenicVariants || 0), 0)}
              </div>
              <div className="text-xs text-red-600 mt-1">Requires attention</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Pharmacogenomics</div>
                <FlaskConical className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {analyses.filter(a => a.pharmacogenomics).length}
              </div>
              <div className="text-xs text-blue-600 mt-1">Drug response tests</div>
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

            {/* Analyses Tab */}
            {activeTab === 'analyses' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading analyses...</div>
                ) : filteredAnalyses.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No analyses found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Analysis Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Variants</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pathogenic</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Score</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredAnalyses.map((analysis) => (
                        <tr key={analysis.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedAnalysis(analysis)}>
                          <td className="px-6 py-4">
                            <div>
                              <div className="font-medium text-gray-900">{analysis.patientName}</div>
                              <div className="text-sm text-gray-500">{analysis.patientId}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{analysis.analysisType}</td>
                          <td className="px-6 py-4 text-sm">{getStatusBadge(analysis.status)}</td>
                          <td className="px-6 py-4 text-sm text-gray-900">{analysis.variants || 0}</td>
                          <td className="px-6 py-4">
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                              {analysis.pathogenicVariants || 0}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskColor(analysis.riskScore || 0)}`}>
                              {((analysis.riskScore || 0) * 100).toFixed(0)}%
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">{analysis.submittedDate}</td>
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

            {/* Variants Tab */}
            {activeTab === 'variants' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading variants...</div>
                ) : variants.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No variants found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gene</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Location</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pathogenicity</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Clinical Significance</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Associated Diseases</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {variants.map((variant) => (
                        <tr key={variant.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 font-medium text-gray-900">{variant.gene}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            Chr {variant.chromosome}:{variant.position}
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                              {variant.variantType}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getPathogenicityColor(variant.pathogenicity)}`}>
                              {variant.pathogenicity}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{variant.clinicalSignificance}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">
                            {variant.diseases?.join(', ') || 'N/A'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Analysis Detail Modal */}
      {selectedAnalysis && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedAnalysis(null)}>
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Analysis Details</h2>
              <button onClick={() => setSelectedAnalysis(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedAnalysis.patientName}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient ID</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedAnalysis.patientId}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Analysis Type</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedAnalysis.analysisType}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Status</div>
                  <div className="mt-1">{getStatusBadge(selectedAnalysis.status)}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Submitted Date</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedAnalysis.submittedDate}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Risk Score</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getRiskColor(selectedAnalysis.riskScore || 0)}`}>
                    {((selectedAnalysis.riskScore || 0) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-3">Variant Summary</div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-700">Total Variants</div>
                    <div className="text-2xl font-bold text-blue-900">{selectedAnalysis.variants || 0}</div>
                  </div>
                  <div className="p-3 bg-yellow-50 rounded-lg">
                    <div className="text-sm text-yellow-700">Clinical Variants</div>
                    <div className="text-2xl font-bold text-yellow-900">{selectedAnalysis.clinicalVariants || 0}</div>
                  </div>
                  <div className="p-3 bg-red-50 rounded-lg">
                    <div className="text-sm text-red-700">Pathogenic</div>
                    <div className="text-2xl font-bold text-red-900">{selectedAnalysis.pathogenicVariants || 0}</div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-3">Key Findings</div>
                <ul className="space-y-2">
                  {selectedAnalysis.findings?.map((finding, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="text-purple-600 mt-1">•</span>
                      <span>{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-medium">
                  Generate Report
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  View Variants
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
