'use client'

import { Activity, Brain, TrendingUp, Pill, Heart, Shield, Zap, Users, ArrowRight, Sparkles, CheckCircle, Star, ChevronRight } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/95 backdrop-blur-sm border-b border-gray-100 z-50">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="bg-blue-600 p-1.5 rounded-lg">
                <Activity className="h-5 w-5 text-white" strokeWidth={2.5} />
              </div>
              <span className="text-lg font-bold text-gray-900">AI Diagnostics</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm font-medium text-gray-600 hover:text-gray-900">Features</a>
              <a href="#how-it-works" className="text-sm font-medium text-gray-600 hover:text-gray-900">How It Works</a>
              <a href="#pricing" className="text-sm font-medium text-gray-600 hover:text-gray-900">Pricing</a>
              <a href="#" className="text-sm font-medium text-gray-600 hover:text-gray-900">Sign In</a>
              <button className="bg-blue-600 text-white px-5 py-2 rounded-lg text-sm font-semibold hover:bg-blue-700 transition">
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            {/* Left Column - Content */}
            <div>
              <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1.5 rounded-full text-sm font-medium mb-6">
                <Sparkles className="h-3.5 w-3.5" />
                <span>New: FDA-Cleared AI Technology</span>
              </div>

              <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                Clinical decisions powered by <span className="text-blue-600">AI</span>
              </h1>

              <p className="text-xl text-gray-600 mb-8 leading-relaxed">
                Transform patient care with advanced machine learning. Accurate disease detection,
                risk assessment, and evidence-based recommendations in seconds.
              </p>

              <div className="flex flex-col sm:flex-row gap-4 mb-8">
                <button className="bg-blue-600 text-white px-8 py-4 rounded-lg font-semibold hover:bg-blue-700 transition flex items-center justify-center gap-2 shadow-lg shadow-blue-600/20">
                  Start Free Trial
                  <ArrowRight className="h-5 w-5" />
                </button>
                <button className="bg-white text-gray-700 px-8 py-4 rounded-lg font-semibold border border-gray-300 hover:bg-gray-50 transition">
                  Watch Demo
                </button>
              </div>

              {/* Trust Badges */}
              <div className="flex items-center gap-6 text-sm text-gray-600">
                <div className="flex items-center gap-1">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>HIPAA Compliant</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>SOC 2 Certified</span>
                </div>
                <div className="flex items-center gap-1">
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  <span>99.9% Uptime</span>
                </div>
              </div>
            </div>

            {/* Right Column - Visual */}
            <div className="relative">
              <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-2xl p-8 shadow-2xl">
                {/* Dashboard Preview */}
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="bg-blue-600 p-2 rounded-lg">
                      <Brain className="h-5 w-5 text-white" />
                    </div>
                    <div>
                      <div className="text-sm font-semibold text-gray-900">Patient Analysis</div>
                      <div className="text-xs text-gray-500">Real-time diagnostic insights</div>
                    </div>
                  </div>

                  {/* Stats Grid */}
                  <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="bg-green-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-green-600">99.7%</div>
                      <div className="text-xs text-gray-600">Accuracy</div>
                    </div>
                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">&lt;2s</div>
                      <div className="text-xs text-gray-600">Response Time</div>
                    </div>
                  </div>

                  {/* Progress Bars */}
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-600">Disease Detection</span>
                        <span className="text-gray-900 font-semibold">97%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-blue-600 rounded-full" style={{width: '97%'}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-600">Risk Assessment</span>
                        <span className="text-gray-900 font-semibold">94%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-green-600 rounded-full" style={{width: '94%'}}></div>
                      </div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-gray-600">Treatment Recommendations</span>
                        <span className="text-gray-900 font-semibold">98%</span>
                      </div>
                      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full bg-purple-600 rounded-full" style={{width: '98%'}}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Floating Stats */}
              <div className="absolute -bottom-6 -left-6 bg-white rounded-xl shadow-xl p-4 border border-gray-100">
                <div className="text-3xl font-bold text-gray-900">1M+</div>
                <div className="text-sm text-gray-600">Diagnoses Processed</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="py-12 bg-gray-50 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <p className="text-center text-sm text-gray-600 mb-8">Trusted by leading healthcare organizations</p>
          <div className="flex justify-center items-center gap-12 flex-wrap opacity-50">
            <div className="text-2xl font-bold text-gray-400">Mayo Clinic</div>
            <div className="text-2xl font-bold text-gray-400">Cleveland Clinic</div>
            <div className="text-2xl font-bold text-gray-400">Johns Hopkins</div>
            <div className="text-2xl font-bold text-gray-400">Stanford Health</div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Everything you need for clinical excellence
            </h2>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Comprehensive AI tools designed to support every aspect of patient care
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="group p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition">
              <div className="bg-blue-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-600 transition">
                <Brain className="h-6 w-6 text-blue-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI Diagnostics</h3>
              <p className="text-gray-600 text-sm">
                99.7% accuracy across 50+ conditions with explainable AI insights
              </p>
            </div>

            <div className="group p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition">
              <div className="bg-green-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-600 transition">
                <TrendingUp className="h-6 w-6 text-green-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Risk Assessment</h3>
              <p className="text-gray-600 text-sm">
                Predictive analytics for proactive patient care management
              </p>
            </div>

            <div className="group p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition">
              <div className="bg-purple-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-600 transition">
                <Heart className="h-6 w-6 text-purple-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Clinical Support</h3>
              <p className="text-gray-600 text-sm">
                Evidence-based treatment recommendations from clinical guidelines
              </p>
            </div>

            <div className="group p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition">
              <div className="bg-orange-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-orange-600 transition">
                <Pill className="h-6 w-6 text-orange-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Drug Discovery</h3>
              <p className="text-gray-600 text-sm">
                AI-powered compound generation and molecular optimization
              </p>
            </div>

            <div className="group p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition">
              <div className="bg-red-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-red-600 transition">
                <Shield className="h-6 w-6 text-red-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">HIPAA Compliant</h3>
              <p className="text-gray-600 text-sm">
                Enterprise security with end-to-end encryption and audit logs
              </p>
            </div>

            <div className="group p-6 bg-white border border-gray-200 rounded-xl hover:shadow-lg transition">
              <div className="bg-indigo-100 w-12 h-12 rounded-lg flex items-center justify-center mb-4 group-hover:bg-indigo-600 transition">
                <Zap className="h-6 w-6 text-indigo-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-Time Analytics</h3>
              <p className="text-gray-600 text-sm">
                Live dashboards with instant insights and automated alerts
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-24 px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              How it works
            </h2>
            <p className="text-lg text-gray-600">
              Get started in minutes, not months
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="relative bg-white p-8 rounded-xl border border-gray-200">
              <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg mb-6">1</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Connect Your Data</h3>
              <p className="text-gray-600">
                Seamlessly integrate with your existing EHR systems and medical devices
              </p>
            </div>

            <div className="relative bg-white p-8 rounded-xl border border-gray-200">
              <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg mb-6">2</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">AI Analysis</h3>
              <p className="text-gray-600">
                Our models analyze patient data in real-time across 50+ conditions
              </p>
            </div>

            <div className="relative bg-white p-8 rounded-xl border border-gray-200">
              <div className="bg-blue-600 text-white w-10 h-10 rounded-full flex items-center justify-center font-bold text-lg mb-6">3</div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">Actionable Insights</h3>
              <p className="text-gray-600">
                Receive evidence-based recommendations to support clinical decisions
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-24 px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Loved by healthcare professionals
            </h2>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-600 mb-4">
                "AI Diagnostics has transformed how we approach patient care. The accuracy is remarkable."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div>
                  <div className="font-semibold text-sm">Dr. Sarah Chen</div>
                  <div className="text-xs text-gray-500">Chief Medical Officer</div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-600 mb-4">
                "The real-time analytics have helped us identify high-risk patients earlier than ever before."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div>
                  <div className="font-semibold text-sm">Dr. Michael Rodriguez</div>
                  <div className="text-xs text-gray-500">Head of Cardiology</div>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
              <div className="flex gap-1 mb-4">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-600 mb-4">
                "Implementation was seamless, and the support team is incredibly responsive."
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gray-200 rounded-full"></div>
                <div>
                  <div className="font-semibold text-sm">Dr. Emily Watson</div>
                  <div className="text-xs text-gray-500">Director of Emergency Medicine</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 lg:px-8 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
            Ready to get started?
          </h2>
          <p className="text-xl text-blue-100 mb-10">
            Join thousands of healthcare providers transforming patient care with AI
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition shadow-xl">
              Start Free Trial
            </button>
            <button className="bg-transparent text-white border-2 border-white px-8 py-4 rounded-lg font-semibold hover:bg-white/10 transition">
              Schedule Demo
            </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="grid md:grid-cols-5 gap-8 mb-12">
            <div className="md:col-span-2">
              <div className="flex items-center gap-2 mb-4">
                <div className="bg-blue-600 p-1.5 rounded-lg">
                  <Activity className="h-5 w-5 text-white" />
                </div>
                <span className="font-bold text-lg">AI Diagnostics</span>
              </div>
              <p className="text-gray-400 text-sm mb-4">
                Advanced clinical decision support powered by machine learning
              </p>
              <p className="text-gray-500 text-xs">
                © 2025 M.Y. Engineering and Technologies
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-sm">Product</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">Features</a></li>
                <li><a href="#" className="hover:text-white transition">Pricing</a></li>
                <li><a href="#" className="hover:text-white transition">Security</a></li>
                <li><a href="#" className="hover:text-white transition">Integrations</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-sm">Company</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">About</a></li>
                <li><a href="#" className="hover:text-white transition">Careers</a></li>
                <li><a href="#" className="hover:text-white transition">Contact</a></li>
                <li><a href="#" className="hover:text-white transition">Blog</a></li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-sm">Legal</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white transition">Privacy</a></li>
                <li><a href="#" className="hover:text-white transition">Terms</a></li>
                <li><a href="#" className="hover:text-white transition">HIPAA</a></li>
                <li><a href="#" className="hover:text-white transition">Compliance</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-400">
              Powered by Advanced Machine Learning
            </p>
            <div className="flex gap-6">
              <a href="#" className="text-gray-400 hover:text-white transition text-sm">Twitter</a>
              <a href="#" className="text-gray-400 hover:text-white transition text-sm">LinkedIn</a>
              <a href="#" className="text-gray-400 hover:text-white transition text-sm">GitHub</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
