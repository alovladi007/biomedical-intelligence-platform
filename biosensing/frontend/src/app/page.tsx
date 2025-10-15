'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Activity, Wifi, Heart, Bell, TrendingUp, Shield, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle, Radio, Zap } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-teal-50">
      {/* Top Contact Bar */}
      <div className="bg-teal-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 789-0123</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>biosensing@medtech.com</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>24/7 Monitoring</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-teal-600 to-green-600 p-2 rounded-lg">
                <Activity className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">Biosensing Technology</div>
                <div className="text-xs text-gray-500">Real-Time Monitoring</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm font-medium text-gray-700 hover:text-teal-600">Features</a>
              <a href="#testimonials" className="text-sm font-medium text-gray-700 hover:text-teal-600">Testimonials</a>
              <Link href="/dashboard" className="text-sm font-medium text-gray-700 hover:text-teal-600">Dashboard</Link>
              <button className="px-5 py-2 bg-teal-600 hover:bg-teal-700 text-white text-sm font-semibold rounded-lg transition shadow-md">
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
                AWS IoT Core • Real-Time Streaming
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                Real-Time Biosensor
                <span className="text-teal-600"> Data Monitoring</span>
              </h1>

              <p className="text-lg text-gray-600">
                Connect biosensors via AWS IoT Core for real-time streaming, automatic alerts, and intelligent anomaly detection with WebSocket updates.
              </p>

              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <Radio className="h-4 w-4" />
                  View Dashboard
                </Link>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-teal-600 hover:text-teal-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            {/* Right: Stats Grid */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Live Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-teal-600">100Hz</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Sampling Rate</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">&lt;50ms</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Latency</div>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-blue-600">24/7</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Monitoring</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-orange-600">99.9%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Uptime</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Trusted by 100+ healthcare facilities</p>
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
                {['overview', 'sensors', 'integration'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-semibold capitalize whitespace-nowrap transition ${
                      activeTab === tab
                        ? 'text-teal-600 border-b-2 border-teal-600 bg-white'
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
                    <h3 className="text-2xl font-bold text-gray-900">Real-Time Patient Monitoring</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Our IoT-powered biosensing platform streams vital signs in real-time, detects anomalies automatically, and alerts clinicians instantly for critical events.
                    </p>
                    <div className="space-y-3">
                      {['AWS IoT Core integration with MQTT', 'WebSocket live streaming updates', 'Automatic anomaly detection and alerts', 'HIPAA compliant data encryption'].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { icon: Wifi, title: 'IoT Connected', color: 'bg-teal-50 text-teal-600' },
                      { icon: Activity, title: 'Live Streaming', color: 'bg-green-50 text-green-600' },
                      { icon: Bell, title: 'Smart Alerts', color: 'bg-orange-50 text-orange-600' },
                      { icon: Shield, title: 'Secure', color: 'bg-red-50 text-red-600' },
                    ].map((item, idx) => (
                      <div key={idx} className={`${item.color} rounded-xl p-5 hover:scale-105 transition cursor-pointer`}>
                        <item.icon className="h-8 w-8 mb-3" />
                        <div className="font-bold text-sm">{item.title}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'sensors' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Supported Biosensors</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { icon: Heart, name: 'ECG', desc: 'Heart rate, rhythm, and cardiac monitoring', color: 'border-red-500' },
                      { icon: Activity, name: 'PPG', desc: 'Blood oxygen saturation and pulse', color: 'border-blue-500' },
                      { icon: TrendingUp, name: 'EEG', desc: 'Brain activity and neural patterns', color: 'border-purple-500' },
                      { icon: Activity, name: 'EMG', desc: 'Muscle activity and movement', color: 'border-green-500' },
                      { icon: Zap, name: 'GSR', desc: 'Skin conductance and stress levels', color: 'border-yellow-500' },
                      { icon: Activity, name: 'Temp', desc: 'Core body temperature tracking', color: 'border-orange-500' },
                    ].map((sensor, idx) => (
                      <div key={idx} className={`border-l-4 ${sensor.color} bg-gray-50 rounded-lg p-5 hover:shadow-lg transition`}>
                        <sensor.icon className="h-8 w-8 text-gray-700 mb-3" />
                        <div className="font-bold text-lg text-gray-900 mb-2">{sensor.name}</div>
                        <div className="text-sm text-gray-600">{sensor.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'integration' && (
                <div className="grid md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h3 className="text-2xl font-bold text-gray-900">AWS IoT Core Integration</h3>
                    <div className="space-y-4">
                      <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">MQTT Protocol</div>
                        <div className="text-sm text-gray-600">Secure bidirectional communication with IoT devices</div>
                      </div>
                      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">WebSocket Streaming</div>
                        <div className="text-sm text-gray-600">Real-time data delivery to web dashboards</div>
                      </div>
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Scalable Architecture</div>
                        <div className="text-sm text-gray-600">Handle millions of messages per second</div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-gray-900">Features</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Complete platform for biosensor data processing, visualization, and clinical decision support.
                    </p>
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                      <div className="space-y-3">
                        {['Real-time data streaming', 'Anomaly detection algorithms', 'Automatic alert generation', 'Historical data analytics', 'Clinical integration ready'].map((item, idx) => (
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
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Trusted by Healthcare Providers</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Dr. Amanda Lee', role: 'ICU Director', quote: 'Real-time monitoring has reduced response times by 65%. Critical alerts reach us instantly.' },
              { name: 'Dr. Carlos Rivera', role: 'Chief of Cardiology', quote: 'The ECG monitoring accuracy is exceptional. We trust it for our most critical patients.' },
              { name: 'Nurse Patricia Kim', role: 'Head of Telemetry', quote: 'Easy to deploy, intuitive dashboard, and reliable 24/7. Best biosensing platform we\'ve used.' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-4">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-teal-500 to-teal-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
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
          <div className="bg-gradient-to-r from-teal-600 to-green-600 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Deploy Real-Time Monitoring?</h2>
            <p className="text-lg mb-6 opacity-90">Join 100+ facilities using our IoT biosensing platform</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/dashboard" className="px-7 py-3 bg-white text-teal-600 font-bold rounded-lg hover:bg-gray-100 transition shadow-xl">
                View Dashboard
              </Link>
              <button className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-teal-600 transition">
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
                <div className="bg-teal-600 p-2 rounded-lg">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">Biosensing Tech</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">Real-time IoT monitoring platform</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 789-0123</div>
                <div>biosensing@medtech.com</div>
              </div>
            </div>

            {[
              { title: 'Services', links: ['IoT Monitoring', 'Data Analytics', 'Alert Systems'] },
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
