'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Shield, Lock, FileText, Users, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle, Eye, Database, AlertTriangle } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-pink-50">
      {/* Top Contact Bar */}
      <div className="bg-red-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 555-1234</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>compliance@healthcare.com</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>24/7 Compliance Support</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-red-600 to-pink-600 p-2 rounded-lg">
                <Shield className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">HIPAA Compliance</div>
                <div className="text-xs text-gray-500">Enterprise Security</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm font-medium text-gray-700 hover:text-red-600">Features</a>
              <a href="#testimonials" className="text-sm font-medium text-gray-700 hover:text-red-600">Testimonials</a>
              <Link href="/dashboard" className="text-sm font-medium text-gray-700 hover:text-red-600">Dashboard</Link>
              <button className="px-5 py-2 bg-red-600 hover:bg-red-700 text-white text-sm font-semibold rounded-lg transition shadow-md">
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
                AES-256-GCM • SOC 2 Certified
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                Enterprise HIPAA
                <span className="text-red-600"> Compliance Platform</span>
              </h1>

              <p className="text-lg text-gray-600">
                Comprehensive audit logging, AES-256-GCM encryption, BAA management, and data breach tracking for healthcare compliance.
              </p>

              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <Shield className="h-4 w-4" />
                  View Dashboard
                </Link>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-red-600 hover:text-red-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Right: Stats Grid */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Compliance Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-red-600">100%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Compliant</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">0</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Breaches</div>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-blue-600">24/7</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Monitoring</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-purple-600">256-bit</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Encryption</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Trusted by 200+ healthcare organizations</p>
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
                {['overview', 'security', 'compliance'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-semibold capitalize whitespace-nowrap transition ${
                      activeTab === tab
                        ? 'text-red-600 border-b-2 border-red-600 bg-white'
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
                    <h3 className="text-2xl font-bold text-gray-900">Complete HIPAA Compliance Solution</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Enterprise-grade platform providing comprehensive audit logging, encryption, BAA management, and breach tracking to ensure full HIPAA compliance.
                    </p>
                    <div className="space-y-3">
                      {['AES-256-GCM encryption for all PHI', 'Comprehensive audit trail logging', 'Automated BAA agreement management', 'Real-time breach detection and tracking'].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { icon: Lock, title: 'Encryption', color: 'bg-red-50 text-red-600' },
                      { icon: FileText, title: 'Audit Logs', color: 'bg-blue-50 text-blue-600' },
                      { icon: Users, title: 'BAA Management', color: 'bg-green-50 text-green-600' },
                      { icon: AlertTriangle, title: 'Breach Tracking', color: 'bg-orange-50 text-orange-600' },
                    ].map((item, idx) => (
                      <div key={idx} className={`${item.color} rounded-xl p-5 hover:scale-105 transition cursor-pointer`}>
                        <item.icon className="h-8 w-8 mb-3" />
                        <div className="font-bold text-sm">{item.title}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'security' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Enterprise Security Features</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { icon: Lock, title: 'AES-256-GCM', desc: 'Military-grade encryption for all PHI data', color: 'border-red-500' },
                      { icon: FileText, title: 'Audit Logging', desc: 'Complete audit trail of all system access', color: 'border-blue-500' },
                      { icon: Eye, title: 'Access Control', desc: 'Role-based access control (RBAC)', color: 'border-green-500' },
                      { icon: Database, title: 'Data Protection', desc: 'Encrypted at rest and in transit', color: 'border-purple-500' },
                      { icon: AlertTriangle, title: 'Breach Detection', desc: 'Real-time threat monitoring', color: 'border-orange-500' },
                      { icon: Shield, title: 'Compliance', desc: 'HIPAA, HITECH, and SOC 2 certified', color: 'border-pink-500' },
                    ].map((feature, idx) => (
                      <div key={idx} className={`border-l-4 ${feature.color} bg-gray-50 rounded-lg p-5 hover:shadow-lg transition`}>
                        <feature.icon className="h-8 w-8 text-gray-700 mb-3" />
                        <div className="font-bold text-lg text-gray-900 mb-2">{feature.title}</div>
                        <div className="text-sm text-gray-600">{feature.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'compliance' && (
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900">HIPAA Compliance Standards</h3>
                    <div className="space-y-4">
                      <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Privacy Rule</div>
                        <div className="text-sm text-gray-600">Protect patient health information privacy</div>
                      </div>
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Security Rule</div>
                        <div className="text-sm text-gray-600">Safeguard electronic PHI with technical controls</div>
                      </div>
                      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Breach Notification</div>
                        <div className="text-sm text-gray-600">Automated breach detection and reporting</div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-gray-900">Compliance Features</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Complete platform for maintaining HIPAA compliance with automated tools for audit, encryption, and breach management.
                    </p>
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                      <div className="space-y-3">
                        {['Automated audit log generation', 'BAA agreement tracking', 'Breach notification workflows', 'Access control management', 'Encryption key management'].map((item, idx) => (
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
              { name: 'Jennifer Thompson', role: 'Chief Compliance Officer', quote: 'Best HIPAA compliance platform we\'ve used. Audit logging is comprehensive and easy to navigate.' },
              { name: 'Dr. Robert Martinez', role: 'Hospital Administrator', quote: 'Encryption and BAA management features have streamlined our compliance workflows significantly.' },
              { name: 'Sarah Johnson', role: 'IT Security Director', quote: 'Real-time breach detection gives us peace of mind. Support team is excellent and responsive.' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-4">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
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
          <div className="bg-gradient-to-r from-red-600 to-pink-600 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready for Complete HIPAA Compliance?</h2>
            <p className="text-lg mb-6 opacity-90">Join 200+ healthcare organizations securing their data</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/dashboard" className="px-7 py-3 bg-white text-red-600 font-bold rounded-lg hover:bg-gray-100 transition shadow-xl">
                View Dashboard
              </Link>
              <button className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-red-600 transition">
                Request Demo
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
                <div className="bg-red-600 p-2 rounded-lg">
                  <Shield className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">HIPAA Compliance</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">Enterprise security platform</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 555-1234</div>
                <div>compliance@healthcare.com</div>
              </div>
            </div>

            {[
              { title: 'Services', links: ['Audit Logging', 'Encryption', 'BAA Management'] },
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
