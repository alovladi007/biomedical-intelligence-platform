'use client'

import { useState } from 'react'
import Link from 'next/link'
import { Heart, Calendar, Activity, Bell, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle, User, FileText } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  return (
    <div className="min-h-screen bg-gradient-to-br from-pink-50 via-white to-rose-50">
      {/* Top Contact Bar */}
      <div className="bg-pink-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 234-5678</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>care@obicare.health</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>Maternal Care 24/7</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-pink-600 to-rose-600 p-2 rounded-lg">
                <Heart className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">OBiCare</div>
                <div className="text-xs text-gray-500">Obstetric Intelligence Care</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm font-medium text-gray-700 hover:text-pink-600">Features</a>
              <a href="#testimonials" className="text-sm font-medium text-gray-700 hover:text-pink-600">Testimonials</a>
              <Link href="/dashboard" className="text-sm font-medium text-gray-700 hover:text-pink-600">Dashboard</Link>
              <button className="px-5 py-2 bg-pink-600 hover:bg-pink-700 text-white text-sm font-semibold rounded-lg transition shadow-md">
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
                HIPAA Compliant • Evidence-Based
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                Comprehensive Maternal
                <span className="text-pink-600"> Health Monitoring</span>
              </h1>

              <p className="text-lg text-gray-600">
                Complete prenatal care platform with appointment management, vital signs tracking, risk assessment, and patient records for better maternal outcomes.
              </p>

              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-6 py-3 bg-pink-600 hover:bg-pink-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <Heart className="h-4 w-4" />
                  Open Dashboard
                </Link>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-pink-600 hover:text-pink-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Care Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-pink-600">5K+</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Mothers</div>
                  </div>
                  <div className="bg-gradient-to-br from-rose-50 to-rose-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-rose-600">98%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Satisfaction</div>
                  </div>
                  <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-blue-600">24/7</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Support</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">100%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Compliant</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Trusted by 100+ healthcare providers</p>
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
                {['overview', 'care', 'features'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-4 text-sm font-semibold capitalize whitespace-nowrap transition ${
                      activeTab === tab
                        ? 'text-pink-600 border-b-2 border-pink-600 bg-white'
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
                    <h3 className="text-2xl font-bold text-gray-900">Complete Prenatal Care Platform</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Comprehensive maternal health monitoring with appointment scheduling, vital signs tracking, risk assessment, and integrated patient records.
                    </p>
                    <div className="space-y-3">
                      {['Prenatal care tracking and management', 'Appointment scheduling and reminders', 'Real-time vital signs monitoring', 'AI-powered risk assessment'].map((item, idx) => (
                        <div key={idx} className="flex items-center gap-3">
                          <CheckCircle className="h-5 w-5 text-green-600 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    {[
                      { icon: Calendar, title: 'Appointments', color: 'bg-pink-50 text-pink-600' },
                      { icon: Activity, title: 'Vital Signs', color: 'bg-rose-50 text-rose-600' },
                      { icon: Bell, title: 'Alerts', color: 'bg-orange-50 text-orange-600' },
                      { icon: FileText, title: 'Records', color: 'bg-blue-50 text-blue-600' },
                    ].map((item, idx) => (
                      <div key={idx} className={`${item.color} rounded-xl p-5 hover:scale-105 transition cursor-pointer`}>
                        <item.icon className="h-8 w-8 mb-3" />
                        <div className="font-bold text-sm">{item.title}</div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'care' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-6">Maternal Care Services</h3>
                  <div className="grid md:grid-cols-3 gap-6">
                    {[
                      { icon: Calendar, title: 'Appointment Management', desc: 'Schedule and track prenatal visits', color: 'border-pink-500' },
                      { icon: Activity, title: 'Vital Signs', desc: 'Monitor blood pressure, weight, heart rate', color: 'border-rose-500' },
                      { icon: Bell, title: 'Risk Alerts', desc: 'AI-powered risk detection and alerts', color: 'border-orange-500' },
                      { icon: FileText, title: 'Medical Records', desc: 'Complete patient history tracking', color: 'border-blue-500' },
                      { icon: User, title: 'Patient Portal', desc: 'Secure access to health information', color: 'border-green-500' },
                      { icon: Heart, title: 'Wellness Tracking', desc: 'Monitor maternal and fetal health', color: 'border-purple-500' },
                    ].map((service, idx) => (
                      <div key={idx} className={`border-l-4 ${service.color} bg-gray-50 rounded-lg p-5 hover:shadow-lg transition`}>
                        <service.icon className="h-8 w-8 text-gray-700 mb-3" />
                        <div className="font-bold text-lg text-gray-900 mb-2">{service.title}</div>
                        <div className="text-sm text-gray-600">{service.desc}</div>
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
                      <div className="bg-gradient-to-br from-pink-50 to-pink-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Prenatal Tracking</div>
                        <div className="text-sm text-gray-600">Complete pregnancy journey monitoring and care coordination</div>
                      </div>
                      <div className="bg-gradient-to-br from-rose-50 to-rose-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Smart Scheduling</div>
                        <div className="text-sm text-gray-600">Automated appointment reminders and calendar integration</div>
                      </div>
                      <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-5">
                        <div className="font-bold text-gray-900 mb-2">Risk Assessment</div>
                        <div className="text-sm text-gray-600">AI-powered early detection of complications</div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="text-xl font-bold text-gray-900">Key Benefits</h3>
                    <p className="text-gray-600 leading-relaxed">
                      Improve maternal outcomes with comprehensive monitoring, timely interventions, and coordinated care.
                    </p>
                    <div className="bg-white border border-gray-200 rounded-xl p-6">
                      <div className="space-y-3">
                        {['Reduced pregnancy complications', 'Better care coordination', 'Improved patient satisfaction', 'HIPAA compliant security', 'Real-time health monitoring'].map((item, idx) => (
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
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Trusted by Expectant Mothers</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Jessica Martinez', role: 'First-Time Mother', quote: 'OBiCare made my pregnancy journey so much easier. The app is intuitive and supportive.' },
              { name: 'Dr. Karen White', role: 'OB-GYN', quote: 'Excellent platform for prenatal monitoring. My patients love the appointment reminders and vitals tracking.' },
              { name: 'Maria Chen', role: 'Expecting Mother', quote: 'The risk assessment feature gave me peace of mind. Care team was always responsive and helpful.' },
            ].map((t, idx) => (
              <div key={idx} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition">
                <div className="flex gap-1 mb-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-sm text-gray-700 italic mb-4">"{t.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-gradient-to-br from-pink-500 to-pink-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
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
          <div className="bg-gradient-to-r from-pink-600 to-rose-600 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready for Better Maternal Care?</h2>
            <p className="text-lg mb-6 opacity-90">Join 5,000+ mothers and 100+ providers using OBiCare</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/dashboard" className="px-7 py-3 bg-white text-pink-600 font-bold rounded-lg hover:bg-gray-100 transition shadow-xl">
                Open Dashboard
              </Link>
              <button className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-pink-600 transition">
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
                <div className="bg-pink-600 p-2 rounded-lg">
                  <Heart className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">OBiCare</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">Obstetric Intelligence Care</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 234-5678</div>
                <div>care@obicare.health</div>
              </div>
            </div>

            {[
              { title: 'Services', links: ['Prenatal Care', 'Appointments', 'Monitoring'] },
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
