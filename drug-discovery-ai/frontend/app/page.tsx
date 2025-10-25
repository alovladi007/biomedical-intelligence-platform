import Link from 'next/link'
import { FlaskConical, Pill, Microscope, TrendingUp, ArrowRight, CheckCircle, Zap, Target, Beaker, Brain, Shield, Users } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 via-white to-teal-50">
      {/* Hero Section */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-cyan-600/10 to-teal-600/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="inline-flex items-center gap-3 mb-6">
              <div className="bg-gradient-to-r from-cyan-600 to-teal-600 p-4 rounded-2xl shadow-lg">
                <FlaskConical className="h-12 w-12 text-white" />
              </div>
              <div className="text-left">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-600 to-teal-600 bg-clip-text text-transparent">
                  Drug Discovery AI
                </h1>
                <p className="text-xl text-gray-600 mt-1">Accelerated Pharmaceutical Research</p>
              </div>
            </div>
            <p className="text-2xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
              Accelerated pharmaceutical research with molecular modeling and clinical trial optimization
            </p>
            <div className="mt-8 flex gap-4 justify-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-cyan-600 to-teal-600 text-white rounded-xl hover:shadow-xl transition-all duration-200 text-lg font-semibold"
              >
                Launch Platform
                <ArrowRight className="h-5 w-5" />
              </Link>
              <a
                href="#features"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-cyan-600 rounded-xl hover:shadow-xl transition-all duration-200 text-lg font-semibold border-2 border-cyan-200"
              >
                Explore Features
              </a>
            </div>
          </div>
        </div>
      </header>

      {/* Key Features Grid */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">AI-Powered Drug Discovery</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Transform pharmaceutical research with cutting-edge AI technologies and predictive modeling
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-cyan-100">
            <div className="bg-cyan-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <Beaker className="h-7 w-7 text-cyan-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Molecular Design Automation</h3>
            <p className="text-gray-600 leading-relaxed">
              AI-driven molecular design and optimization for lead compounds
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-teal-100">
            <div className="bg-teal-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <Users className="h-7 w-7 text-teal-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Clinical Trial Matching</h3>
            <p className="text-gray-600 leading-relaxed">
              Intelligent patient matching and trial optimization
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-blue-100">
            <div className="bg-blue-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <Shield className="h-7 w-7 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Adverse Event Prediction</h3>
            <p className="text-gray-600 leading-relaxed">
              Predictive models for safety and toxicity assessment
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-purple-100">
            <div className="bg-purple-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <Pill className="h-7 w-7 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Drug Repurposing Algorithms</h3>
            <p className="text-gray-600 leading-relaxed">
              Discover new applications for existing therapeutics
            </p>
          </div>
        </div>
      </section>

      {/* AI Capabilities */}
      <section className="bg-gradient-to-r from-cyan-600 to-teal-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Advanced AI Capabilities</h2>
            <p className="text-xl text-cyan-100">Comprehensive drug discovery and development platform</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Brain className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Molecular Modeling</h3>
              <p className="text-cyan-100 mb-4">Advanced computational chemistry and structure prediction</p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Structure-based design</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Binding affinity prediction</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>ADMET profiling</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Virtual screening</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Target className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Target Identification</h3>
              <p className="text-cyan-100 mb-4">AI-powered target discovery and validation</p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Pathway analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Protein interactions</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Disease associations</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Druggability scoring</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Zap className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Lead Optimization</h3>
              <p className="text-cyan-100 mb-4">Accelerate lead compound development</p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Property optimization</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Synthesis planning</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Selectivity tuning</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Off-target prediction</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Shield className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Safety Prediction</h3>
              <p className="text-cyan-100 mb-4">Early identification of safety risks</p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Toxicity prediction</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Cardiotoxicity screening</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Hepatotoxicity alerts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Drug-drug interactions</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Users className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Clinical Trials</h3>
              <p className="text-cyan-100 mb-4">Optimize clinical trial design and execution</p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Patient stratification</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Endpoint selection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Enrollment prediction</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Adaptive trials</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Pill className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Drug Repurposing</h3>
              <p className="text-cyan-100 mb-4">Identify new therapeutic applications</p>
              <ul className="space-y-2 text-cyan-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Network analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Indication expansion</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Literature mining</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Real-world evidence</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Platform Benefits */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Platform Benefits</h2>
          <p className="text-xl text-gray-600">Accelerate drug discovery from target to clinic</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-br from-cyan-50 to-cyan-100 rounded-2xl p-8 border border-cyan-200">
            <TrendingUp className="h-12 w-12 text-cyan-600 mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">70% Faster</h3>
            <p className="text-gray-700 mb-4">Accelerate drug discovery timelines from years to months</p>
            <div className="flex items-center gap-2 text-cyan-600 font-semibold">
              <CheckCircle className="h-5 w-5" />
              <span>Proven results</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-teal-50 to-teal-100 rounded-2xl p-8 border border-teal-200">
            <Microscope className="h-12 w-12 text-teal-600 mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">60% Cost Reduction</h3>
            <p className="text-gray-700 mb-4">Significantly reduce R&D costs through AI optimization</p>
            <div className="flex items-center gap-2 text-teal-600 font-semibold">
              <CheckCircle className="h-5 w-5" />
              <span>Cost effective</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 border border-blue-200">
            <Target className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Higher Success Rate</h3>
            <p className="text-gray-700 mb-4">Improve clinical trial success rates with predictive AI</p>
            <div className="flex items-center gap-2 text-blue-600 font-semibold">
              <CheckCircle className="h-5 w-5" />
              <span>Data driven</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-cyan-600 to-teal-600 rounded-3xl p-12 text-center shadow-2xl">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Accelerate Drug Discovery?</h2>
          <p className="text-xl text-cyan-100 mb-8 max-w-2xl mx-auto">
            Transform pharmaceutical research with our AI-powered drug discovery platform
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-cyan-600 rounded-xl hover:shadow-xl transition-all duration-200 text-lg font-semibold"
          >
            Get Started Now
            <ArrowRight className="h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FlaskConical className="h-8 w-8 text-cyan-400" />
              <div>
                <div className="font-bold text-lg">Drug Discovery AI</div>
                <div className="text-sm text-gray-400">Accelerated Pharmaceutical Research</div>
              </div>
            </div>
            <div className="text-sm text-gray-400">
              © 2025 Biomedical Intelligence Platform. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
