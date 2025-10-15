'use client'

import { useState } from 'react'
import { Brain, TrendingUp, Pill, Heart, Shield, Zap, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle, Sparkles } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Top Contact Bar */}
      <div className="bg-blue-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 123-4567</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>info@aidiagnostics.com</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>Available 24/7</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-2 rounded-lg">
                <Brain className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">AI Diagnostics</div>
                <div className="text-xs text-gray-500">Clinical Intelligence</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm font-medium text-gray-700 hover:text-blue-600">Features</a>
              <a href="#testimonials" className="text-sm font-medium text-gray-700 hover:text-blue-600">Testimonials</a>
              <a href="#" className="text-sm font-medium text-gray-700 hover:text-blue-600">Contact</a>
              <button className="px-5 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-semibold rounded-lg transition shadow-md">
                Get Started
              </button>
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
                FDA-Cleared • HIPAA Compliant
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                Clinical Decisions Powered by
                <span className="text-blue-600"> Artificial Intelligence</span>
              </h1>

              <p className="text-lg text-gray-600">
                Transform patient care with advanced machine learning. Accurate disease detection, risk assessment, and evidence-based clinical recommendations.
              </p>

              <div className="flex flex-wrap gap-3">
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <Sparkles className="h-4 w-4" />
                  Start Free Trial
                </button>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-blue-600 hover:text-blue-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Right: Stats Grid */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Platform Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-blue-600">10+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Years</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">500+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Partners</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-purple-600">1M+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Diagnoses</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-orange-600">99.7%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Accuracy</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Rated 5.0 by 200+ professionals</p>
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
                {['overview', 'capabilities', 'technology'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-semibold capitalize whitespace-nowrap transition ${
                      activeTab === tab
                        ? 'text-blue-600 border-b-2 border-blue-600 bg-white'
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
                    <h3 className="text-2xl font-bold text-gray-900">AI-Powered Clinical Excellence</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Our platform combines cutting-edge machine learning with clinical expertise to deliver accurate diagnoses, proactive risk assessment, and personalized treatment recommendations.
                    </p>
                    <div className="space-y-3">
                      {['50+ conditions detected with 99.7% accuracy', 'Real-time risk assessment and alerts', 'Evidence-based treatment recommendations', 'HIPAA compliant with SOC 2 certification'].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { icon: Brain, title: 'AI Diagnostics', color: 'bg-blue-50 text-blue-600' },
                      { icon: TrendingUp, title: 'Risk Analysis', color: 'bg-green-50 text-green-600' },
                      { icon: Heart, title: 'Clinical Support', color: 'bg-pink-50 text-pink-600' },
                      { icon: Shield, title: 'Security', color: 'bg-red-50 text-red-600' },
                    ].map((item, idx) => (
                      <div key={idx} className={`${item.color} rounded-xl p-5 hover:scale-105 transition cursor-pointer`}>
                        <item.icon className="h-8 w-8 mb-3" />
                        <div className="font-bold text-sm">{item.title}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'capabilities' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Core Capabilities</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      {
                        icon: Brain,
                        title: 'Disease Detection',
                        desc: '99.7% accuracy across 50+ medical conditions',
                        color: 'border-blue-500'
                      },
                      {
                        icon: TrendingUp,
                        title: 'Predictive Analytics',
                        desc: 'Identify high-risk patients proactively',
                        color: 'border-green-500'
                      },
                      {
                        icon: Heart,
                        title: 'Treatment Plans',
                        desc: 'Evidence-based clinical recommendations',
                        color: 'border-pink-500'
                      },
                      {
                        icon: Pill,
                        title: 'Drug Discovery',
                        desc: 'AI-powered compound generation',
                        color: 'border-orange-500'
                      },
                      {
                        icon: Shield,
                        title: 'Data Security',
                        desc: 'Enterprise-grade protection',
                        color: 'border-red-500'
                      },
                      {
                        icon: Zap,
                        title: 'Real-Time Insights',
                        desc: 'Instant analysis and alerts',
                        color: 'border-purple-500'
                      },
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

              {activeTab === 'technology' && (
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900">Advanced AI Technology</h3>
                    <div className="space-y-4">
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Deep Learning Models</div>
                        <div className="text-sm text-gray-600">State-of-the-art neural networks trained on millions of cases</div>
                      </div>
                      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Explainable AI</div>
                        <div className="text-sm text-gray-600">Transparent decision-making with full audit trails</div>
                      </div>
                      <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Continuous Learning</div>
                        <div className="text-sm text-gray-600">Models improve with each new case analyzed</div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-gray-900">Integration</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Seamlessly connects with your existing healthcare infrastructure including EHR systems, medical devices, and clinical workflows.
                    </p>
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                      <div className="space-y-3">
                        {['EHR/EMR Systems', 'Medical Device APIs', 'PACS Integration', 'HL7/FHIR Standards', 'Cloud & On-Premise'].map((item, idx) => (
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

      {/* Testimonials - Compact */}
      <section id="testimonials" className="py-8 px-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Trusted by Healthcare Leaders</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Dr. Sarah Chen', role: 'Chief Medical Officer', quote: 'AI Diagnostics has transformed our approach to patient care. Remarkable accuracy.' },
              { name: 'Dr. Michael Rodriguez', role: 'Head of Cardiology', quote: 'Real-time analytics help us identify high-risk patients earlier than ever.' },
              { name: 'Dr. Emily Watson', role: 'Director of Emergency Medicine', quote: 'Seamless implementation and incredibly responsive support team.' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-4">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
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
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Transform Patient Care?</h2>
            <p className="text-lg mb-6 opacity-90">Join 500+ healthcare organizations improving outcomes with AI</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <button className="px-7 py-3 bg-white text-blue-600 font-bold rounded-lg hover:bg-gray-100 transition shadow-xl">
                Start Free Trial
              </button>
              <button className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-blue-600 transition">
                Schedule Demo
              </button>
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
                <div className="bg-blue-600 p-2 rounded-lg">
                  <Brain className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">AI Diagnostics</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">Clinical intelligence powered by AI</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 123-4567</div>
                <div>info@aidiagnostics.com</div>
              </div>
            </div>

            {[
              { title: 'Services', links: ['AI Diagnostics', 'Risk Assessment', 'Clinical Support'] },
              { title: 'Company', links: ['About', 'Careers', 'Contact'] },
              { title: 'Legal', links: ['Privacy', 'Terms', 'HIPAA'] },
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
