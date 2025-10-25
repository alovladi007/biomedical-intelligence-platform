'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Cpu, FlaskConical, Rocket, TrendingUp, Home, Database, Settings, Search, CheckCircle, Clock, XCircle, Play, Package } from 'lucide-react'

interface Experiment {
  id: string
  name: string
  description: string
  status: string
  accuracy: number
  loss: number
  epoch: number
  totalEpochs: number
  createdAt: string
  framework: string
  dataset: string
}

interface Model {
  id: string
  name: string
  version: string
  framework: string
  accuracy: number
  size: string
  status: string
  deployments: number
  lastUpdated: string
}

interface Deployment {
  id: string
  modelName: string
  environment: string
  status: string
  requests: number
  latency: number
  uptime: number
  deployedAt: string
}

export default function Dashboard() {
  const [experiments, setExperiments] = useState<Experiment[]>([])
  const [models, setModels] = useState<Model[]>([])
  const [deployments, setDeployments] = useState<Deployment[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedExperiment, setSelectedExperiment] = useState<Experiment | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'experiments' | 'models' | 'deployments'>('experiments')

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:5005/api/v1/experiments').then(res => res.json()),
      fetch('http://localhost:5005/api/v1/models').then(res => res.json()),
      fetch('http://localhost:5005/api/v1/deployments').then(res => res.json())
    ])
      .then(([experimentsData, modelsData, deploymentsData]) => {
        setExperiments(experimentsData.experiments || [])
        setModels(modelsData.models || [])
        setDeployments(deploymentsData.deployments || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setLoading(false)
      })
  }, [])

  const filteredExperiments = experiments.filter(exp =>
    exp.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    exp.framework?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'completed': return <div className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-600" /><span className="text-green-600">Completed</span></div>
      case 'running': return <div className="flex items-center gap-1"><Play className="h-4 w-4 text-blue-600" /><span className="text-blue-600">Running</span></div>
      case 'failed': return <div className="flex items-center gap-1"><XCircle className="h-4 w-4 text-red-600" /><span className="text-red-600">Failed</span></div>
      case 'pending': return <div className="flex items-center gap-1"><Clock className="h-4 w-4 text-yellow-600" /><span className="text-yellow-600">Pending</span></div>
      default: return <span className="text-gray-600">Unknown</span>
    }
  }

  const getFrameworkColor = (framework: string) => {
    switch(framework) {
      case 'PyTorch': return 'bg-orange-100 text-orange-800'
      case 'TensorFlow': return 'bg-yellow-100 text-yellow-800'
      case 'JAX': return 'bg-blue-100 text-blue-800'
      case 'scikit-learn': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getEnvironmentColor = (env: string) => {
    switch(env) {
      case 'production': return 'bg-green-100 text-green-800'
      case 'staging': return 'bg-yellow-100 text-yellow-800'
      case 'development': return 'bg-blue-100 text-blue-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-gradient-to-br from-orange-600 to-red-600 p-2 rounded-lg">
              <Cpu className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">BioTensor Labs</div>
              <div className="text-xs text-gray-500">ML Platform</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('experiments')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'experiments'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FlaskConical className="h-5 w-5" />
              Experiments
            </button>
            <button
              onClick={() => setActiveTab('models')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'models'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Package className="h-5 w-5" />
              Model Registry
            </button>
            <button
              onClick={() => setActiveTab('deployments')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'deployments'
                  ? 'bg-orange-50 text-orange-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Rocket className="h-5 w-5" />
              Deployments
            </button>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Database className="h-5 w-5" />
              Datasets
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <TrendingUp className="h-5 w-5" />
              Metrics
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
              <h1 className="text-2xl font-bold text-gray-900">BioTensor Labs Dashboard</h1>
              <p className="text-sm text-gray-500">ML experiments, model registry, and deployment pipeline</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium">
                New Experiment
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Total Experiments</div>
                <FlaskConical className="h-5 w-5 text-orange-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{experiments.length}</div>
              <div className="text-xs text-green-600 mt-1">+12 this week</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Registered Models</div>
                <Package className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{models.length}</div>
              <div className="text-xs text-blue-600 mt-1">Ready to deploy</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Deployments</div>
                <Rocket className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {deployments.filter(d => d.status === 'running').length}
              </div>
              <div className="text-xs text-green-600 mt-1">In production</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Avg Accuracy</div>
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {experiments.filter(e => e.status === 'completed').length > 0
                  ? `${(experiments.filter(e => e.status === 'completed').reduce((acc, e) => acc + e.accuracy, 0) / experiments.filter(e => e.status === 'completed').length * 100).toFixed(1)}%`
                  : '0%'
                }
              </div>
              <div className="text-xs text-purple-600 mt-1">Across all models</div>
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
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                />
              </div>
            </div>

            {/* Experiments Tab */}
            {activeTab === 'experiments' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading experiments...</div>
                ) : filteredExperiments.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No experiments found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Framework</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Dataset</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Progress</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Accuracy</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Loss</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredExperiments.map((exp) => (
                        <tr key={exp.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedExperiment(exp)}>
                          <td className="px-6 py-4">
                            <div>
                              <div className="font-medium text-gray-900">{exp.name}</div>
                              <div className="text-sm text-gray-500">{exp.description}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getFrameworkColor(exp.framework)}`}>
                              {exp.framework}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{exp.dataset}</td>
                          <td className="px-6 py-4">
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div
                                className="bg-orange-600 h-2 rounded-full"
                                style={{ width: `${(exp.epoch / exp.totalEpochs) * 100}%` }}
                              ></div>
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              {exp.epoch}/{exp.totalEpochs} epochs
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {exp.status === 'completed' ? `${(exp.accuracy * 100).toFixed(2)}%` : '-'}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">
                            {exp.status === 'completed' ? exp.loss.toFixed(4) : '-'}
                          </td>
                          <td className="px-6 py-4 text-sm">
                            {getStatusBadge(exp.status)}
                          </td>
                          <td className="px-6 py-4">
                            <button className="text-orange-600 hover:text-orange-800 text-sm font-medium">
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

            {/* Models Tab */}
            {activeTab === 'models' && (
              <div className="p-6">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading models...</div>
                ) : models.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No models registered</div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {models.map((model) => (
                      <div key={model.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <div className="font-semibold text-gray-900">{model.name}</div>
                            <div className="text-sm text-gray-500">Version {model.version}</div>
                          </div>
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getFrameworkColor(model.framework)}`}>
                            {model.framework}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 mb-3">
                          <div>
                            <div className="text-xs text-gray-500">Accuracy</div>
                            <div className="text-sm font-semibold text-gray-900">{(model.accuracy * 100).toFixed(1)}%</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Size</div>
                            <div className="text-sm font-semibold text-gray-900">{model.size}</div>
                          </div>
                          <div>
                            <div className="text-xs text-gray-500">Deployments</div>
                            <div className="text-sm font-semibold text-gray-900">{model.deployments}</div>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="text-xs text-gray-500">Updated {model.lastUpdated}</div>
                          <button className="px-3 py-1 text-sm text-orange-600 hover:bg-orange-50 rounded-lg font-medium">
                            Deploy
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Deployments Tab */}
            {activeTab === 'deployments' && (
              <div className="p-6">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading deployments...</div>
                ) : deployments.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No active deployments</div>
                ) : (
                  <div className="space-y-3">
                    {deployments.map((deployment) => (
                      <div key={deployment.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <Rocket className="h-5 w-5 text-orange-600" />
                            <div>
                              <div className="font-semibold text-gray-900">{deployment.modelName}</div>
                              <div className="text-sm text-gray-500">Deployed {deployment.deployedAt}</div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getEnvironmentColor(deployment.environment)}`}>
                              {deployment.environment}
                            </span>
                            {getStatusBadge(deployment.status)}
                          </div>
                        </div>
                        <div className="grid grid-cols-4 gap-4 text-sm">
                          <div>
                            <span className="text-gray-500">Requests:</span>
                            <span className="ml-2 font-medium text-gray-900">{deployment.requests.toLocaleString()}</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Latency:</span>
                            <span className="ml-2 font-medium text-gray-900">{deployment.latency}ms</span>
                          </div>
                          <div>
                            <span className="text-gray-500">Uptime:</span>
                            <span className="ml-2 font-medium text-gray-900">{deployment.uptime}%</span>
                          </div>
                          <div>
                            <button className="text-orange-600 hover:text-orange-800 font-medium">
                              Manage
                            </button>
                          </div>
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

      {/* Experiment Detail Modal */}
      {selectedExperiment && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedExperiment(null)}>
          <div className="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Experiment Details</h2>
              <button onClick={() => setSelectedExperiment(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedExperiment.name}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Framework</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getFrameworkColor(selectedExperiment.framework)}`}>
                    {selectedExperiment.framework}
                  </span>
                </div>
                <div className="col-span-2">
                  <div className="text-sm font-medium text-gray-500">Description</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedExperiment.description}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Dataset</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedExperiment.dataset}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Status</div>
                  <div className="mt-1">{getStatusBadge(selectedExperiment.status)}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Created</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedExperiment.createdAt}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Progress</div>
                  <div className="text-lg font-semibold text-gray-900">
                    {selectedExperiment.epoch}/{selectedExperiment.totalEpochs} epochs
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-3">Performance Metrics</div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="text-sm text-green-700 mb-1">Accuracy</div>
                    <div className="text-2xl font-bold text-green-900">
                      {selectedExperiment.status === 'completed'
                        ? `${(selectedExperiment.accuracy * 100).toFixed(2)}%`
                        : 'In progress...'
                      }
                    </div>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-700 mb-1">Loss</div>
                    <div className="text-2xl font-bold text-blue-900">
                      {selectedExperiment.status === 'completed'
                        ? selectedExperiment.loss.toFixed(4)
                        : 'In progress...'
                      }
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium">
                  View Logs
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  Register Model
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
