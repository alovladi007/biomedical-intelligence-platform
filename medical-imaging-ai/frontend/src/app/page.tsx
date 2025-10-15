'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Activity, Upload, Image, Brain, FileText, TrendingUp, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-blue-50">
      {/* Top Contact Bar */}
      <div className="bg-indigo-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 456-7890</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>imaging@medicalai.com</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>24/7 Support</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 p-2 rounded-lg">
                <Brain className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">Medical Imaging AI</div>
                <div className="text-xs text-gray-500">Diagnostic Radiology</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <Link href="/worklist" className="text-sm font-medium text-gray-700 hover:text-indigo-600">Worklist</Link>
              <Link href="/patients" className="text-sm font-medium text-gray-700 hover:text-indigo-600">Patients</Link>
              <Link href="/upload" className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-lg transition">
                Upload DICOM
              </Link>
            </div>

            <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - Compact */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-5 gap-8">
            {/* Left: Main Info */}
            <div className="lg:col-span-3 space-y-6">
              <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 px-3 py-1.5 rounded-full text-xs font-semibold">
                <CheckCircle className="h-3.5 w-3.5" />
                FDA-Cleared • PACS Integrated
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                AI-Powered Medical Imaging Analysis
              </h1>

              <p className="text-lg text-gray-600">
                Advanced DICOM analysis with explainable AI (Grad-CAM), automatic triage, and seamless PACS integration.
              </p>

              <div className="flex flex-wrap gap-3">
                <Link href="/upload" className="inline-flex items-center gap-2 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <Upload className="h-4 w-4" />
                  Upload DICOM
                </Link>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-indigo-600 hover:text-indigo-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Right: Stats Grid */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Platform Statistics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-indigo-600">14+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Pathologies</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">95.8%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Accuracy</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-purple-600">3</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Modalities</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-orange-600">&lt;2s</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Speed</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Trusted by 150+ hospitals</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Tabs Section */}
      <section className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
            {/* Tabs */}
            <div className="border-b border-gray-200 bg-gray-50">
              <div className="flex overflow-x-auto">
                {['overview', 'models', 'features'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-semibold capitalize whitespace-nowrap transition ${
                      activeTab === tab
                        ? 'text-indigo-600 border-b-2 border-indigo-600 bg-white'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
            </div>

            {/* Tab Content */}
            <div className="p-8">
              {activeTab === 'overview' && (
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-2xl font-bold text-gray-900">Comprehensive Imaging Platform</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Our AI-powered platform provides radiologists with advanced diagnostic tools including Grad-CAM visualizations, automatic triage, and seamless PACS integration.
                    </p>
                    <div className="space-y-3">
                      {['DICOM compliant viewer', 'Explainable AI with Grad-CAM', 'Automatic priority assignment', 'Real-time PACS integration'].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { icon: Image, title: 'DICOM Viewer', color: 'bg-blue-50 text-blue-600' },
                      { icon: Brain, title: 'Grad-CAM', color: 'bg-green-50 text-green-600' },
                      { icon: Activity, title: 'Auto Triage', color: 'bg-purple-50 text-purple-600' },
                      { icon: Upload, title: 'PACS Sync', color: 'bg-orange-50 text-orange-600' },
                    ].map((item, idx) => (
                      <div key={idx} className={`${item.color} rounded-xl p-5 hover:scale-105 transition cursor-pointer`}>
                        <item.icon className="h-8 w-8 mb-3" />
                        <div className="font-bold text-sm">{item.title}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'models' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">AI Models</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      {
                        name: 'ResNet50',
                        type: 'Chest X-Ray',
                        accuracy: '96.2%',
                        desc: '14-class pathology detection',
                        color: 'border-blue-500'
                      },
                      {
                        name: 'EfficientNet-B0',
                        type: 'CT Scan',
                        accuracy: '94.8%',
                        desc: 'COVID-19 detection',
                        color: 'border-green-500'
                      },
                      {
                        name: 'DenseNet121',
                        type: 'Brain MRI',
                        accuracy: '97.1%',
                        desc: 'Tumor classification',
                        color: 'border-purple-500'
                      },
                    ].map((model, idx) => (
                      <div key={idx} className={`border-l-4 ${model.color} bg-gray-50 rounded-lg p-5 hover:shadow-lg transition`}>
                        <div className="font-bold text-lg text-gray-900">{model.name}</div>
                        <div className="text-sm text-gray-600 mb-3">{model.type}</div>
                        <div className="text-xs text-gray-600 mb-3">{model.desc}</div>
                        <div className="flex justify-between items-center pt-3 border-t border-gray-300">
                          <span className="text-xs text-gray-600">Accuracy</span>
                          <span className="font-bold text-green-600">{model.accuracy}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'features' && (
                <div className="grid md:grid-cols-3 gap-6">
                  {[
                    { icon: Image, title: 'DICOM Viewer', desc: 'Full-featured viewer with pan, zoom, rotate' },
                    { icon: Brain, title: 'Grad-CAM AI', desc: 'Explainable AI with heatmap visualizations' },
                    { icon: Activity, title: 'Auto Triage', desc: 'Priority assignment: critical, urgent, routine' },
                    { icon: TrendingUp, title: 'Multi-Model', desc: 'ResNet, EfficientNet, DenseNet support' },
                    { icon: FileText, title: 'Clinical Reports', desc: 'Structured findings and recommendations' },
                    { icon: Upload, title: 'PACS Integration', desc: 'C-FIND/C-MOVE for query and retrieve' },
                  ].map((feature, idx) => (
                    <div key={idx} className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-xl p-5 hover:shadow-xl transition">
                      <feature.icon className="h-10 w-10 text-indigo-600 mb-3" />
                      <h4 className="font-bold text-gray-900 mb-2">{feature.title}</h4>
                      <p className="text-sm text-gray-600">{feature.desc}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials - Compact */}
      <section className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Trusted by Radiologists</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Dr. James Peterson', role: 'Chief Radiologist', quote: 'Grad-CAM visualization is a game-changer for explaining AI predictions.' },
              { name: 'Dr. Lisa Martinez', role: 'Director of Imaging', quote: 'PACS integration was seamless. Reduced response time by 70%.' },
              { name: 'Dr. Robert Chen', role: 'Interventional Radiologist', quote: 'Unified platform for X-Ray, CT, and MRI. Highly efficient.' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-4">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
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

      {/* CTA - Compact */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-lg mb-6 opacity-90">Join 150+ radiology departments using AI for better diagnostics</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/upload" className="px-7 py-3 bg-white text-indigo-600 font-bold rounded-lg hover:bg-gray-100 transition">
                Upload DICOM Now
              </Link>
              <Link href="/worklist" className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-indigo-600 transition">
                View Worklist
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer - Compact */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid md:grid-cols-4 gap-8 mb-8">
            <div className="md:col-span-1">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-indigo-600 p-2 rounded-lg">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">Medical Imaging AI</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">Advanced diagnostic imaging with AI</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 456-7890</div>
                <div>imaging@medicalai.com</div>
              </div>
            </div>

            {[
              { title: 'Services', links: ['DICOM Viewer', 'AI Analysis', 'PACS Integration'] },
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
