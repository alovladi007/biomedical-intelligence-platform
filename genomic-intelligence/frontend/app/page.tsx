import Link from 'next/link'
import { Dna, Microscope, FlaskConical, Users, ArrowRight, CheckCircle, TrendingUp, Database, Zap, Shield, Globe } from 'lucide-react'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
      {/* Hero Section */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-blue-600/10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
          <div className="text-center">
            <div className="inline-flex items-center gap-3 mb-6">
              <div className="bg-gradient-to-r from-purple-600 to-blue-600 p-4 rounded-2xl shadow-lg">
                <Dna className="h-12 w-12 text-white" />
              </div>
              <div className="text-left">
                <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  Genomic Intelligence
                </h1>
                <p className="text-xl text-gray-600 mt-1">Precision Medicine Platform</p>
              </div>
            </div>
            <p className="text-2xl text-gray-700 max-w-3xl mx-auto leading-relaxed">
              Personalized medicine platform with pharmacogenomics and precision therapeutics
            </p>
            <div className="mt-8 flex gap-4 justify-center">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-xl hover:shadow-xl transition-all duration-200 text-lg font-semibold"
              >
                Launch Platform
                <ArrowRight className="h-5 w-5" />
              </Link>
              <a
                href="#features"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-purple-600 rounded-xl hover:shadow-xl transition-all duration-200 text-lg font-semibold border-2 border-purple-200"
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
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Revolutionary Genomic Analysis</h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Pioneering genomic technologies for precision medicine, including novel sequencing methods, variant interpretation, and pharmacogenomic applications
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-purple-100">
            <div className="bg-purple-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <CheckCircle className="h-7 w-7 text-purple-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Variant Interpretation</h3>
            <p className="text-gray-600 leading-relaxed">
              Comprehensive variant interpretation and pathogenicity assessment
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-blue-100">
            <div className="bg-blue-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <FlaskConical className="h-7 w-7 text-blue-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Drug Response Prediction</h3>
            <p className="text-gray-600 leading-relaxed">
              Personalized medicine through pharmacogenomic analysis
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-green-100">
            <div className="bg-green-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <Microscope className="h-7 w-7 text-green-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Rare Disease Diagnosis</h3>
            <p className="text-gray-600 leading-relaxed">
              Advanced diagnostic tools for rare genetic conditions
            </p>
          </div>

          <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-200 border border-orange-100">
            <div className="bg-orange-100 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
              <Users className="h-7 w-7 text-orange-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900 mb-3">Population Genomics</h3>
            <p className="text-gray-600 leading-relaxed">
              Large-scale population studies and genetic diversity analysis
            </p>
          </div>
        </div>
      </section>

      {/* Genomics Innovation Features */}
      <section className="bg-gradient-to-r from-purple-600 to-blue-600 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-white mb-4">Genomics Innovation Features</h2>
            <p className="text-xl text-purple-100">Cutting-edge genomic technologies for precision medicine</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Zap className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Next-Gen Sequencing</h3>
              <p className="text-purple-100 mb-4">Advanced sequencing technologies for comprehensive genomic analysis</p>
              <ul className="space-y-2 text-purple-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Whole genome sequencing</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Exome sequencing</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>RNA sequencing</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Single-cell analysis</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <Database className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Variant Analysis</h3>
              <p className="text-purple-100 mb-4">Comprehensive variant interpretation and pathogenicity assessment</p>
              <ul className="space-y-2 text-purple-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>SNV detection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>CNV analysis</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Structural variants</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Pathogenicity scoring</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <FlaskConical className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Pharmacogenomics</h3>
              <p className="text-purple-100 mb-4">Personalized medicine through drug response prediction and optimization</p>
              <ul className="space-y-2 text-purple-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Drug metabolism</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Response prediction</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Dosage optimization</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Adverse reactions</span>
                </li>
              </ul>
            </div>

            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <div className="bg-white/20 w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                <TrendingUp className="h-7 w-7 text-white" />
              </div>
              <h3 className="text-xl font-bold text-white mb-4">Research Applications</h3>
              <p className="text-purple-100 mb-4">Advanced genomic research applications and methodologies</p>
              <ul className="space-y-2 text-purple-100">
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Population genomics</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Cancer genomics</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>Rare disease research</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-white mt-1">•</span>
                  <span>GWAS studies</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Research Applications */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-4">Research Applications</h2>
          <p className="text-xl text-gray-600">Advanced genomic research applications and methodologies</p>
        </div>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 border border-blue-200">
            <Globe className="h-12 w-12 text-blue-600 mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Population Genomics</h3>
            <p className="text-gray-700 mb-6">Large-scale population studies and genetic diversity analysis</p>
            <div className="flex flex-wrap gap-2">
              <span className="px-4 py-2 bg-blue-200 text-blue-800 rounded-lg font-semibold text-sm">GWAS</span>
              <span className="px-4 py-2 bg-blue-200 text-blue-800 rounded-lg font-semibold text-sm">Population Studies</span>
              <span className="px-4 py-2 bg-blue-200 text-blue-800 rounded-lg font-semibold text-sm">Diversity</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-2xl p-8 border border-red-200">
            <Microscope className="h-12 w-12 text-red-600 mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Cancer Genomics</h3>
            <p className="text-gray-700 mb-6">Comprehensive cancer genomic analysis and biomarker discovery</p>
            <div className="flex flex-wrap gap-2">
              <span className="px-4 py-2 bg-red-200 text-red-800 rounded-lg font-semibold text-sm">Tumor Analysis</span>
              <span className="px-4 py-2 bg-red-200 text-red-800 rounded-lg font-semibold text-sm">Biomarkers</span>
              <span className="px-4 py-2 bg-red-200 text-red-800 rounded-lg font-semibold text-sm">Therapy</span>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-2xl p-8 border border-purple-200">
            <Shield className="h-12 w-12 text-purple-600 mb-4" />
            <h3 className="text-2xl font-bold text-gray-900 mb-3">Rare Disease Genomics</h3>
            <p className="text-gray-700 mb-6">Diagnosis and research for rare genetic diseases and conditions</p>
            <div className="flex flex-wrap gap-2">
              <span className="px-4 py-2 bg-purple-200 text-purple-800 rounded-lg font-semibold text-sm">Diagnosis</span>
              <span className="px-4 py-2 bg-purple-200 text-purple-800 rounded-lg font-semibold text-sm">Rare Diseases</span>
              <span className="px-4 py-2 bg-purple-200 text-purple-800 rounded-lg font-semibold text-sm">Research</span>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-3xl p-12 text-center shadow-2xl">
          <h2 className="text-4xl font-bold text-white mb-4">Ready to Transform Genomic Medicine?</h2>
          <p className="text-xl text-purple-100 mb-8 max-w-2xl mx-auto">
            Start leveraging our comprehensive genomic intelligence platform for precision medicine and personalized therapeutics
          </p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 px-8 py-4 bg-white text-purple-600 rounded-xl hover:shadow-xl transition-all duration-200 text-lg font-semibold"
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
              <Dna className="h-8 w-8 text-purple-400" />
              <div>
                <div className="font-bold text-lg">Genomic Intelligence</div>
                <div className="text-sm text-gray-400">Precision Medicine Platform</div>
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
