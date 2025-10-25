'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { FlaskConical, Activity, TrendingUp, Pill, Home, Beaker, Settings, Search, CheckCircle, Clock, XCircle, Eye, Target } from 'lucide-react'

interface DrugProject {
  id: string
  projectName: string
  targetProtein: string
  stage: string
  leadCompounds: number
  status: string
  probability: number
  indication: string
  predictedEfficacy: number
  toxicityScore: number
}

interface Molecule {
  id: string
  projectId: string
  compoundId: string
  molecularWeight: number
  drugLikeness: number
  bindingAffinity: number
  toxicityPrediction: string
  status: string
}

export default function Dashboard() {
  const [projects, setProjects] = useState<DrugProject[]>([])
  const [molecules, setMolecules] = useState<Molecule[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedProject, setSelectedProject] = useState<DrugProject | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'projects' | 'molecules'>('projects')

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:5008/api/v1/projects').then(res => res.json()),
      fetch('http://localhost:5008/api/v1/molecules').then(res => res.json())
    ])
      .then(([projectsData, moleculesData]) => {
        setProjects(projectsData.projects || [])
        setMolecules(moleculesData.molecules || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setLoading(false)
      })
  }, [])

  const filteredProjects = projects.filter(p =>
    p.projectName?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.targetProtein?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'active': return <div className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-600" /><span className="text-green-600">Active</span></div>
      case 'paused': return <div className="flex items-center gap-1"><Clock className="h-4 w-4 text-yellow-600" /><span className="text-yellow-600">Paused</span></div>
      case 'completed': return <div className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-blue-600" /><span className="text-blue-600">Completed</span></div>
      default: return <span className="text-gray-600">Unknown</span>
    }
  }

  const getStageColor = (stage: string) => {
    const stageColors: Record<string, string> = {
      'Lead Discovery': 'bg-purple-100 text-purple-800',
      'Lead Optimization': 'bg-blue-100 text-blue-800',
      'Preclinical': 'bg-cyan-100 text-cyan-800',
      'Clinical Trial Phase I': 'bg-green-100 text-green-800',
      'Clinical Trial Phase II': 'bg-teal-100 text-teal-800',
      'Clinical Trial Phase III': 'bg-emerald-100 text-emerald-800'
    }
    return stageColors[stage] || 'bg-gray-100 text-gray-800'
  }

  const getToxicityColor = (score: number) => {
    if (score >= 0.7) return 'text-red-600 bg-red-50'
    if (score >= 0.3) return 'text-yellow-600 bg-yellow-50'
    return 'text-green-600 bg-green-50'
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-cyan-600 p-2 rounded-lg">
              <FlaskConical className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">Drug Discovery AI</div>
              <div className="text-xs text-gray-500">Pharma Research</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('projects')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'projects' ? 'bg-cyan-50 text-cyan-600' : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Activity className="h-5 w-5" />
              Projects
            </button>
            <button
              onClick={() => setActiveTab('molecules')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'molecules' ? 'bg-cyan-50 text-cyan-600' : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Beaker className="h-5 w-5" />
              Molecules
            </button>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Target className="h-5 w-5" />
              Clinical Trials
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Pill className="h-5 w-5" />
              Repurposing
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
              <h1 className="text-2xl font-bold text-gray-900">Drug Discovery Dashboard</h1>
              <p className="text-sm text-gray-500">AI-powered pharmaceutical research platform</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 font-medium">
                New Project
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Projects</div>
                <Activity className="h-5 w-5 text-cyan-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{projects.filter(p => p.status === 'active').length}</div>
              <div className="text-xs text-green-600 mt-1">Ongoing research</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Lead Compounds</div>
                <Beaker className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {projects.reduce((sum, p) => sum + (p.leadCompounds || 0), 0)}
              </div>
              <div className="text-xs text-blue-600 mt-1">Under evaluation</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Avg Success Rate</div>
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {projects.length > 0 ? `${((projects.reduce((sum, p) => sum + (p.probability || 0), 0) / projects.length) * 100).toFixed(0)}%` : '0%'}
              </div>
              <div className="text-xs text-green-600 mt-1">Probability</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Clinical Trials</div>
                <Target className="h-5 w-5 text-purple-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {projects.filter(p => p.stage?.includes('Clinical')).length}
              </div>
              <div className="text-xs text-purple-600 mt-1">In progress</div>
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
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-cyan-500 focus:border-cyan-500"
                />
              </div>
            </div>

            {/* Projects Tab */}
            {activeTab === 'projects' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading projects...</div>
                ) : filteredProjects.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No projects found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Project</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Target</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Stage</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Leads</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Success Rate</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Efficacy</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredProjects.map((project) => (
                        <tr key={project.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedProject(project)}>
                          <td className="px-6 py-4">
                            <div>
                              <div className="font-medium text-gray-900">{project.projectName}</div>
                              <div className="text-sm text-gray-500">{project.indication}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{project.targetProtein}</td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getStageColor(project.stage)}`}>
                              {project.stage}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{project.leadCompounds}</td>
                          <td className="px-6 py-4 text-sm">{getStatusBadge(project.status)}</td>
                          <td className="px-6 py-4">
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-blue-100 text-blue-800">
                              {((project.probability || 0) * 100).toFixed(0)}%
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                              {((project.predictedEfficacy || 0) * 100).toFixed(0)}%
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <button className="text-cyan-600 hover:text-cyan-800 text-sm font-medium flex items-center gap-1">
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

            {/* Molecules Tab */}
            {activeTab === 'molecules' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading molecules...</div>
                ) : molecules.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No molecules found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Compound ID</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MW</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Binding Affinity</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Drug-Likeness</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Toxicity</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {molecules.map((mol) => (
                        <tr key={mol.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4 font-medium text-gray-900">{mol.compoundId}</td>
                          <td className="px-6 py-4 text-sm text-gray-600">{mol.molecularWeight?.toFixed(2) || 'N/A'}</td>
                          <td className="px-6 py-4 text-sm text-gray-900">{mol.bindingAffinity?.toFixed(1) || 'N/A'} kcal/mol</td>
                          <td className="px-6 py-4">
                            <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                              {((mol.drugLikeness || 0) * 100).toFixed(0)}%
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                              mol.toxicityPrediction === 'Low' ? 'bg-green-100 text-green-800' :
                              mol.toxicityPrediction === 'Very Low' ? 'bg-blue-100 text-blue-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {mol.toxicityPrediction}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{mol.status}</td>
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

      {/* Project Detail Modal */}
      {selectedProject && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedProject(null)}>
          <div className="bg-white rounded-lg max-w-4xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Project Details</h2>
              <button onClick={() => setSelectedProject(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Project Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedProject.projectName}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Target Protein</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedProject.targetProtein}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Stage</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getStageColor(selectedProject.stage)}`}>
                    {selectedProject.stage}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Status</div>
                  <div className="mt-1">{getStatusBadge(selectedProject.status)}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Indication</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedProject.indication}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Lead Compounds</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedProject.leadCompounds}</div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-3">Performance Metrics</div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-700">Success Probability</div>
                    <div className="text-2xl font-bold text-blue-900">{((selectedProject.probability || 0) * 100).toFixed(0)}%</div>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg">
                    <div className="text-sm text-green-700">Predicted Efficacy</div>
                    <div className="text-2xl font-bold text-green-900">{((selectedProject.predictedEfficacy || 0) * 100).toFixed(0)}%</div>
                  </div>
                  <div className="p-3 bg-yellow-50 rounded-lg">
                    <div className="text-sm text-yellow-700">Toxicity Score</div>
                    <div className="text-2xl font-bold text-yellow-900">{((selectedProject.toxicityScore || 0) * 100).toFixed(0)}%</div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-cyan-600 text-white rounded-lg hover:bg-cyan-700 font-medium">
                  View Molecules
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
