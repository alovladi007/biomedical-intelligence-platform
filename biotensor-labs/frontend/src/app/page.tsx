'use client'

import { useState } from 'react'
import Link from 'next/link'
import { FlaskConical, GitBranch, Package, TrendingUp, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle, Zap, Database } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-indigo-50">
      {/* Top Contact Bar */}
      <div className="bg-purple-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 987-6543</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>labs@biotensor.ai</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>MLOps Support 24/7</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-purple-600 to-indigo-600 p-2 rounded-lg">
                <FlaskConical className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">BioTensor Labs</div>
                <div className="text-xs text-gray-500">MLOps Platform</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm font-medium text-gray-700 hover:text-purple-600">Features</a>
              <a href="#testimonials" className="text-sm font-medium text-gray-700 hover:text-purple-600">Testimonials</a>
              <Link href="/dashboard" className="text-sm font-medium text-gray-700 hover:text-purple-600">Dashboard</Link>
              <button className="px-5 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-semibold rounded-lg transition shadow-md">
                Get Started
              </button>
            </div>

            <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-5 gap-8">
            <div className="lg:col-span-3 space-y-6">
              <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 px-3 py-1.5 rounded-full text-xs font-semibold">
                <CheckCircle className="h-3.5 w-3.5" />
                MLflow Integration • Production Ready
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                MLOps Platform for
                <span className="text-purple-600"> Biomedical AI</span>
              </h1>

              <p className="text-lg text-gray-600">
                Complete MLOps platform with MLflow integration, experiment tracking, model registry, and biomedical signal processing pipelines.
              </p>

              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-6 py-3 bg-purple-600 hover:bg-purple-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <FlaskConical className="h-4 w-4" />
                  Open Labs
                </Link>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-purple-600 hover:text-purple-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Platform Stats</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-purple-600">500+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Experiments</div>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-blue-600">50+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Models</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">100%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Reproducible</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-orange-600">24/7</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Available</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Used by 50+ research teams</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Tabs */}
      <section className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
            <div className="border-b border-gray-200 bg-gray-50">
              <div className="flex overflow-x-auto">
                {['overview', 'mlops', 'features'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-semibold capitalize whitespace-nowrap transition ${
                      activeTab === tab
                        ? 'text-purple-600 border-b-2 border-purple-600 bg-white'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>

            <div className="p-8">
              {activeTab === 'overview' && (
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-2xl font-bold text-gray-900">Complete MLOps Solution</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Enterprise MLOps platform with MLflow integration for experiment tracking, model versioning, and biomedical signal processing.
                    </p>
                    <div className="space-y-3">
                      {['MLflow experiment tracking', 'Model registry and versioning', 'Biomedical signal processing', 'Automated ML pipelines'].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { icon: FlaskConical, title: 'Experiments', color: 'bg-purple-50 text-purple-600' },
                      { icon: Package, title: 'Models', color: 'bg-blue-50 text-blue-600' },
                      { icon: GitBranch, title: 'Versioning', color: 'bg-green-50 text-green-600' },
                      { icon: Zap, title: 'Pipelines', color: 'bg-orange-50 text-orange-600' },
                    ].map((item, idx) => (
                      <div key={idx} className={`${item.color} rounded-xl p-5 hover:scale-105 transition cursor-pointer`}>
                        <item.icon className="h-8 w-8 mb-3" />
                        <div className="font-bold text-sm">{item.title}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'mlops' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">MLOps Capabilities</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { icon: FlaskConical, title: 'Experiment Tracking', desc: 'Track parameters, metrics, and artifacts', color: 'border-purple-500' },
                      { icon: Package, title: 'Model Registry', desc: 'Centralized model versioning and deployment', color: 'border-blue-500' },
                      { icon: GitBranch, title: 'Version Control', desc: 'Complete lineage tracking for reproducibility', color: 'border-green-500' },
                      { icon: Database, title: 'Data Management', desc: 'Biomedical signal data pipelines', color: 'border-orange-500' },
                      { icon: Zap, title: 'Auto ML Pipelines', desc: 'Automated training and evaluation', color: 'border-pink-500' },
                      { icon: TrendingUp, title: 'Performance Metrics', desc: 'Real-time monitoring and visualization', color: 'border-indigo-500' },
                    ].map((cap, idx) => (
                      <div key={idx} className={`border-l-4 ${cap.color} bg-gray-50 rounded-lg p-5 hover:shadow-lg transition`}>
                        <cap.icon className="h-8 w-8 text-gray-700 mb-3" />
                        <div className="font-bold text-lg text-gray-900 mb-2">{cap.title}</div>
                        <div className="text-sm text-gray-600">{cap.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'features' && (
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900">Platform Features</h3>
                    <div className="space-y-4">
                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">MLflow Integration</div>
                        <div className="text-sm text-gray-600">Full integration with MLflow for tracking and registry</div>
                      </div>
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Signal Processing</div>
                        <div className="text-sm text-gray-600">Advanced biomedical signal analysis pipelines</div>
                      </div>
                      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Reproducibility</div>
                        <div className="text-sm text-gray-600">Complete experiment reproducibility guaranteed</div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-gray-900">Key Benefits</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Streamline your ML workflow with automated experiment tracking, model management, and deployment pipelines.
                    </p>
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                      <div className="space-y-3">
                        {['Automated experiment logging', 'Model versioning and registry', 'Hyperparameter optimization', 'Performance visualization', 'Deployment automation'].map((item, idx) => (
                          <div key={idx} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
                            <span className="text-sm text-gray-700">{item}</span>
                            <CheckCircle className="h-5 w-5 text-green-600" />
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Trusted by Research Teams</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Dr. Alan Kim', role: 'ML Research Lead', quote: 'BioTensor Labs has revolutionized our ML workflow. Experiment tracking is seamless.' },
              { name: 'Prof. Maria Santos', role: 'Biomedical Engineering', quote: 'Model registry and versioning features are outstanding. Highly recommended.' },
              { name: 'Dr. James Wilson', role: 'Data Science Director', quote: 'Best MLOps platform for biomedical research. Excellent reproducibility.' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-4">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {t.name.split(' ').map(n => n[0]).join('')}
                  </div>
                  <div>
                    <div className="font-bold text-sm text-gray-900">{t.name}</div>
                    <div className="text-xs text-gray-600">{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Scale Your ML Research?</h2>
            <p className="text-lg mb-6 opacity-90">Join 50+ research teams using BioTensor Labs</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/dashboard" className="px-7 py-3 bg-white text-purple-600 font-bold rounded-lg hover:bg-gray-100 transition shadow-xl">
                Open Labs
              </Link>
              <button className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-purple-600 transition">
                Request Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-purple-600 p-2 rounded-lg">
                  <FlaskConical className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">BioTensor Labs</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">MLOps for biomedical AI</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 987-6543</div>
                <div>labs@biotensor.ai</div>
              </div>
            </div>

            {[
              { title: 'Services', links: ['Experiments', 'Models', 'Pipelines'] },
              { title: 'Company', links: ['About', 'Careers', 'Contact'] },
              { title: 'Legal', links: ['Privacy', 'Terms', 'Compliance'] },
            ].map((col, idx) => (
              <div key={idx}>
                <h3 className="font-bold mb-3 text-sm">{col.title}</h3>
                <ul className="space-y-2">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#" className="text-xs text-gray-400 hover:text-white transition">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-gray-800 pt-6 text-center text-xs text-gray-400">
            © 2025 M.Y. Engineering and Technologies. All rights reserved.
          </div>
        </div>
      </footer>
    </div>
  )
}
