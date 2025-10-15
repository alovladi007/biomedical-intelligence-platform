'use client'

import { useState, useEffect } from 'react'
import { Brain, TrendingUp, Pill, Heart, Shield, Zap, ArrowRight, Sparkles, CheckCircle, Star, Menu, X, Play } from 'lucide-react'

export default function Home() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 -left-4 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute top-0 -right-4 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Navigation */}
      <nav className={`fixed top-0 w-full z-50 transition-all duration-300 ${scrolled ? 'bg-slate-900/80 backdrop-blur-xl border-b border-white/10 shadow-2xl' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl blur opacity-75"></div>
                <div className="relative bg-gradient-to-r from-purple-600 to-blue-600 p-2 rounded-xl">
                  <Brain className="h-6 w-6 text-white" strokeWidth={2.5} />
                </div>
              </div>
              <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">AI Diagnostics</span>
            </div>

            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">How It Works</a>
              <a href="#pricing" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Pricing</a>
              <a href="#" className="text-sm font-medium text-gray-300 hover:text-white transition-colors">Sign In</a>
              <button className="relative group">
                <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl blur opacity-75 group-hover:opacity-100 transition"></div>
                <div className="relative px-6 py-2.5 bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl text-white font-semibold text-sm">
                  Get Started
                </div>
              </button>
            </div>

            <button className="md:hidden" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
              {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden bg-slate-900/95 backdrop-blur-xl border-t border-white/10">
            <div className="px-6 py-4 space-y-3">
              <a href="#features" className="block text-sm font-medium text-gray-300 hover:text-white transition-colors py-2">Features</a>
              <a href="#how-it-works" className="block text-sm font-medium text-gray-300 hover:text-white transition-colors py-2">How It Works</a>
              <a href="#pricing" className="block text-sm font-medium text-gray-300 hover:text-white transition-colors py-2">Pricing</a>
              <a href="#" className="block text-sm font-medium text-gray-300 hover:text-white transition-colors py-2">Sign In</a>
              <button className="w-full bg-gradient-to-r from-purple-600 to-blue-600 px-6 py-2.5 rounded-xl text-white font-semibold text-sm">
                Get Started
              </button>
            </div>
          </div>
        )}
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column */}
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 bg-white/10 backdrop-blur-md border border-white/20 px-4 py-2 rounded-full text-sm font-medium">
                <Sparkles className="h-4 w-4 text-purple-400" />
                <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">New: FDA-Cleared AI Technology</span>
              </div>

              <h1 className="text-5xl lg:text-7xl font-extrabold leading-tight">
                <span className="bg-gradient-to-r from-white via-purple-200 to-blue-200 bg-clip-text text-transparent">
                  Clinical decisions
                </span>
                <br />
                <span className="bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent">
                  powered by AI
                </span>
              </h1>

              <p className="text-xl text-gray-300 leading-relaxed max-w-xl">
                Transform patient care with advanced machine learning. Accurate disease detection, risk assessment, and evidence-based recommendations in seconds.
              </p>

              <div className="flex flex-col sm:flex-row gap-4">
                <button className="group relative">
                  <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-75 group-hover:opacity-100 transition"></div>
                  <div className="relative flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl text-white font-semibold shadow-2xl">
                    Start Free Trial
                    <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                  </div>
                </button>
                <button className="flex items-center justify-center gap-2 px-8 py-4 bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl font-semibold hover:bg-white/20 transition">
                  <Play className="h-5 w-5" />
                  Watch Demo
                </button>
              </div>

              {/* Trust Badges */}
              <div className="flex flex-wrap items-center gap-6 pt-4">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-5 w-5 text-green-400" />
                  <span className="text-gray-300">HIPAA Compliant</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-5 w-5 text-green-400" />
                  <span className="text-gray-300">SOC 2 Certified</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-5 w-5 text-green-400" />
                  <span className="text-gray-300">99.9% Uptime</span>
                </div>
              </div>
            </div>

            {/* Right Column - Dashboard Preview */}
            <div className="relative">
              {/* Glow Effect */}
              <div className="absolute inset-0 bg-gradient-to-r from-purple-500/30 to-blue-500/30 rounded-3xl blur-3xl"></div>

              {/* Glass Card */}
              <div className="relative bg-white/10 backdrop-blur-xl border border-white/20 rounded-3xl p-8 shadow-2xl">
                <div className="bg-gradient-to-br from-purple-900/50 to-blue-900/50 backdrop-blur-sm rounded-2xl p-6 border border-white/10">
                  {/* Header */}
                  <div className="flex items-center gap-3 mb-6">
                    <div className="bg-gradient-to-r from-purple-500 to-blue-500 p-2.5 rounded-xl">
                      <Brain className="h-6 w-6 text-white" />
                    </div>
                    <div>
                      <div className="text-sm font-bold text-white">Patient Analysis</div>
                      <div className="text-xs text-gray-400">Real-time diagnostic insights</div>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-gradient-to-br from-green-500/20 to-emerald-500/20 backdrop-blur-sm p-4 rounded-xl border border-green-500/30">
                      <div className="text-3xl font-bold text-green-400 mb-1">99.7%</div>
                      <div className="text-xs text-gray-300">Accuracy</div>
                    </div>
                    <div className="bg-gradient-to-br from-blue-500/20 to-cyan-500/20 backdrop-blur-sm p-4 rounded-xl border border-blue-500/30">
                      <div className="text-3xl font-bold text-blue-400 mb-1">&lt;2s</div>
                      <div className="text-xs text-gray-300">Response Time</div>
                    </div>
                  </div>

                  {/* Progress Bars */}
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-gray-300">Disease Detection</span>
                        <span className="text-white font-semibold">97%</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full" style={{width: '97%'}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-gray-300">Risk Assessment</span>
                        <span className="text-white font-semibold">94%</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full" style={{width: '94%'}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-2">
                        <span className="text-gray-300">Treatment Recommendations</span>
                        <span className="text-white font-semibold">98%</span>
                      </div>
                      <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-pink-500 to-purple-500 rounded-full" style={{width: '98%'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Stat Card */}
              <div className="absolute -bottom-6 -left-6 bg-white/10 backdrop-blur-xl border border-white/20 rounded-2xl p-5 shadow-2xl">
                <div className="text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">1M+</div>
                <div className="text-sm text-gray-300">Diagnoses Processed</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-16 px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <p className="text-center text-sm text-gray-400 mb-8">Trusted by leading healthcare organizations</p>
          <div className="flex justify-center items-center gap-12 flex-wrap">
            {['Mayo Clinic', 'Cleveland Clinic', 'Johns Hopkins', 'Stanford Health'].map((org) => (
              <div key={org} className="text-2xl font-bold text-gray-500/50 hover:text-gray-400 transition-colors cursor-pointer">
                {org}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold mb-4">
              <span className="bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
                Everything you need for
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                clinical excellence
              </span>
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Comprehensive AI tools designed to support every aspect of patient care
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: Brain, title: 'AI Diagnostics', desc: '99.7% accuracy across 50+ conditions with explainable AI insights', color: 'from-blue-500 to-cyan-500' },
              { icon: TrendingUp, title: 'Risk Assessment', desc: 'Predictive analytics for proactive patient care management', color: 'from-green-500 to-emerald-500' },
              { icon: Heart, title: 'Clinical Support', desc: 'Evidence-based treatment recommendations from clinical guidelines', color: 'from-pink-500 to-rose-500' },
              { icon: Pill, title: 'Drug Discovery', desc: 'AI-powered compound generation and molecular optimization', color: 'from-orange-500 to-amber-500' },
              { icon: Shield, title: 'HIPAA Compliant', desc: 'Enterprise security with end-to-end encryption and audit logs', color: 'from-red-500 to-pink-500' },
              { icon: Zap, title: 'Real-Time Analytics', desc: 'Live dashboards with instant insights and automated alerts', color: 'from-purple-500 to-indigo-500' },
            ].map((feature, idx) => (
              <div key={idx} className="group relative">
                <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 blur-xl transition-opacity" style={{background: `linear-gradient(to right, var(--tw-gradient-stops))`}}></div>
                <div className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all hover:scale-105 hover:border-white/20">
                  <div className={`bg-gradient-to-r ${feature.color} w-12 h-12 rounded-xl flex items-center justify-center mb-4 shadow-lg`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-gray-400 text-sm leading-relaxed">{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              How it works
            </h2>
            <p className="text-lg text-gray-400">
              Get started in minutes, not months
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { num: '1', title: 'Connect Your Data', desc: 'Seamlessly integrate with your existing EHR systems and medical devices' },
              { num: '2', title: 'AI Analysis', desc: 'Our models analyze patient data in real-time across 50+ conditions' },
              { num: '3', title: 'Actionable Insights', desc: 'Receive evidence-based recommendations to support clinical decisions' },
            ].map((step, idx) => (
              <div key={idx} className="relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-8 hover:bg-white/10 transition-all">
                <div className="absolute -top-5 left-8 bg-gradient-to-r from-purple-600 to-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg shadow-lg">
                  {step.num}
                </div>
                <h3 className="text-xl font-bold text-white mb-3 mt-4">{step.title}</h3>
                <p className="text-gray-400 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-6 lg:px-8 relative">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl lg:text-5xl font-bold mb-4 bg-gradient-to-r from-white to-gray-400 bg-clip-text text-transparent">
              Loved by healthcare professionals
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {[
              { name: 'Dr. Sarah Chen', role: 'Chief Medical Officer', quote: 'AI Diagnostics has transformed how we approach patient care. The accuracy is remarkable.' },
              { name: 'Dr. Michael Rodriguez', role: 'Head of Cardiology', quote: 'The real-time analytics have helped us identify high-risk patients earlier than ever before.' },
              { name: 'Dr. Emily Watson', role: 'Director of Emergency Medicine', quote: 'Implementation was seamless, and the support team is incredibly responsive.' },
            ].map((testimonial, idx) => (
              <div key={idx} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition-all">
                <div className="flex gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-gray-300 mb-6 leading-relaxed">"{testimonial.quote}"</p>
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-blue-500 rounded-full"></div>
                  <div>
                    <div className="font-semibold text-white">{testimonial.name}</div>
                    <div className="text-sm text-gray-400">{testimonial.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 lg:px-8 relative">
        <div className="max-w-4xl mx-auto text-center">
          <div className="relative bg-gradient-to-r from-purple-600/20 to-blue-600/20 backdrop-blur-xl border border-white/20 rounded-3xl p-12 shadow-2xl">
            <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-blue-600/10 rounded-3xl blur-2xl"></div>
            <div className="relative">
              <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-white to-gray-300 bg-clip-text text-transparent">
                Ready to get started?
              </h2>
              <p className="text-xl text-gray-300 mb-10">
                Join thousands of healthcare providers transforming patient care with AI
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <button className="group relative">
                  <div className="absolute -inset-1 bg-gradient-to-r from-purple-600 to-blue-600 rounded-2xl blur opacity-75 group-hover:opacity-100 transition"></div>
                  <div className="relative px-8 py-4 bg-white text-purple-600 rounded-2xl font-bold shadow-xl">
                    Start Free Trial
                  </div>
                </button>
                <button className="px-8 py-4 bg-white/10 backdrop-blur-sm border-2 border-white/30 rounded-2xl font-bold hover:bg-white/20 transition">
                  Schedule Demo
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-black/40 backdrop-blur-xl border-t border-white/10 py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-5 gap-8 mb-12">
            <div className="md:col-span-2">
              <div className="flex items-center gap-3 mb-4">
                <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-2 rounded-xl">
                  <Brain className="h-6 w-6 text-white" />
                </div>
                <span className="font-bold text-lg">AI Diagnostics</span>
              </div>
              <p className="text-gray-400 text-sm mb-4 max-w-xs">
                Advanced clinical decision support powered by machine learning
              </p>
              <p className="text-gray-500 text-xs">
                © 2025 M.Y. Engineering and Technologies
              </p>
            </div>

            {[
              { title: 'Product', links: ['Features', 'Pricing', 'Security', 'Integrations'] },
              { title: 'Company', links: ['About', 'Careers', 'Contact', 'Blog'] },
              { title: 'Legal', links: ['Privacy', 'Terms', 'HIPAA', 'Compliance'] },
            ].map((col, idx) => (
              <div key={idx}>
                <h3 className="font-semibold mb-4 text-sm text-white">{col.title}</h3>
                <ul className="space-y-2">
                  {col.links.map((link) => (
                    <li key={link}>
                      <a href="#" className="text-sm text-gray-400 hover:text-white transition-colors">{link}</a>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">
              Powered by Advanced Machine Learning
            </p>
            <div className="flex gap-6">
              {['Twitter', 'LinkedIn', 'GitHub'].map((social) => (
                <a key={social} href="#" className="text-gray-400 hover:text-white transition-colors text-sm">{social}</a>
              ))}
            </div>
          </div>
        </div>
      </footer>

      <style jsx>{`
        @keyframes blob {
          0% { transform: translate(0px, 0px) scale(1); }
          33% { transform: translate(30px, -50px) scale(1.1); }
          66% { transform: translate(-20px, 20px) scale(0.9); }
          100% { transform: translate(0px, 0px) scale(1); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  )
}
