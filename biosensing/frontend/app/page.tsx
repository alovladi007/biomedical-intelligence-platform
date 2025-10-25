'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Activity, Radio, Zap, Wifi, CheckCircle, Star, Menu, X, Phone, Mail, Clock, PlayCircle, ArrowRight } from 'lucide-react'

export default function Home() {
  const [activeTab, setActiveTab] = useState('overview')
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    fetch('http://localhost:5003/health')
      .then(res => res.json())
      .then(data => console.log('Backend connected:', data))
      .catch(err => console.log('Backend not available'));
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-teal-50 via-white to-teal-50">
      {/* Top Contact Bar */}
      <div className="bg-teal-600 text-white py-2.5">
        <div className="max-w-7xl mx-auto px-6 flex flex-wrap justify-between items-center text-sm gap-3">
          <div className="flex items-center gap-5">
            <div className="flex items-center gap-2">
              <Phone className="h-3.5 w-3.5" />
              <span>(800) 100-2000</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="h-3.5 w-3.5" />
              <span>support@biomedical.com</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-3.5 w-3.5" />
            <span>Enterprise Support 24/7</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="bg-white shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2.5">
              <div className="bg-gradient-to-br from-teal-600 to-teal-700 p-2 rounded-lg">
                <Activity className="h-6 w-6 text-white" strokeWidth={2.5} />
              </div>
              <div>
                <div className="text-lg font-bold text-gray-900">Biosensing Technology</div>
                <div className="text-xs text-gray-500">Real-Time Health Monitoring</div>
              </div>
            </div>

            <div className="hidden md:flex items-center gap-6">
              <a href="#features" className="text-sm font-medium text-gray-700 hover:text-teal-600">Features</a>
              <a href="#about" className="text-sm font-medium text-gray-700 hover:text-teal-600">About</a>
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

      {/* Hero Section */}
      <section className="py-12 px-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-5 gap-8">
            <div className="lg:col-span-3 space-y-6">
              <div className="inline-flex items-center gap-2 bg-green-50 border border-green-200 text-green-700 px-3 py-1.5 rounded-full text-xs font-semibold">
                <CheckCircle className="h-3.5 w-3.5" />
                Production Ready • Enterprise Grade
              </div>

              <h1 className="text-4xl lg:text-5xl font-extrabold text-gray-900 leading-tight">
                Advanced
                <span className="text-teal-600"> Biosensing Technology</span>
              </h1>

              <p className="text-lg text-gray-600">
                Comprehensive real-time health monitoring with advanced features, real-time monitoring, and enterprise-grade security.
              </p>

              <div className="flex flex-wrap gap-3">
                <Link href="/dashboard" className="inline-flex items-center gap-2 px-6 py-3 bg-teal-600 hover:bg-teal-700 text-white font-semibold rounded-lg transition shadow-lg">
                  <Activity className="h-4 w-4" />
                  Open Dashboard
                </Link>
                <button className="inline-flex items-center gap-2 px-6 py-3 bg-white border-2 border-gray-300 text-gray-700 font-semibold rounded-lg hover:border-teal-600 hover:text-teal-600 transition">
                  <PlayCircle className="h-4 w-4" />
                  Watch Demo
                </button>
              </div>
            </div>

            <div className="lg:col-span-2">
              <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Platform Metrics</h3>
                <div className="grid grid-cols-2 gap-4">
                  <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-teal-600">99.9%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Uptime</div>
                  </div>
                  <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-green-600">100%</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">HIPAA</div>
                  </div>
                  <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-purple-600">AI/ML</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Powered</div>
                  </div>
                  <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-xl p-4 text-center">
                    <div className="text-3xl font-extrabold text-orange-600">24/7</div>
                    <div className="text-xs text-gray-600 font-medium mt-1">Support</div>
                  </div>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-200 text-center">
                  <div className="flex justify-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <p className="text-xs text-gray-600">Trusted by healthcare providers</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-8 px-6 bg-white">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">Platform Features</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5, 6].map((item) => (
              <div key={item} className="bg-gradient-to-br from-gray-50 to-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition">
                <div className="text-3xl mb-3">🔬</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">Feature {item}</h3>
                <p className="text-sm text-gray-600">Advanced capability with enterprise features and real-time monitoring.</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-12 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="bg-gradient-to-r from-teal-600 to-teal-700 rounded-2xl p-10 text-center text-white shadow-2xl">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Ready to Get Started?</h2>
            <p className="text-lg mb-6 opacity-90">Experience the power of Biosensing Technology</p>
            <div className="flex flex-wrap gap-4 justify-center">
              <Link href="/dashboard" className="px-7 py-3 bg-white text-teal-600 font-bold rounded-lg hover:bg-gray-100 transition shadow-xl">
                Open Dashboard
              </Link>
              <button className="px-7 py-3 bg-transparent border-2 border-white text-white font-bold rounded-lg hover:bg-white hover:text-teal-600 transition">
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
            <div>
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-teal-600 p-2 rounded-lg">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                <div className="font-bold">Biosensing Technology</div>
              </div>
              <p className="text-sm text-gray-400 mb-3">Real-Time Health Monitoring</p>
              <div className="text-xs text-gray-400 space-y-1">
                <div>(800) 100-2000</div>
                <div>support@biomedical.com</div>
              </div>
            </div>

            {[
              { title: 'Product', links: ['Features', 'Pricing', 'Security'] },
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
