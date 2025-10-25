'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Heart, Calendar, Activity, Bell, Home, Users, FileText, Settings, Search, AlertTriangle, TrendingUp, Phone } from 'lucide-react'

interface Patient {
  id: string
  name: string
  age: number
  gestationalWeek: number
  dueDate: string
  riskLevel: string
  bloodType: string
  lastVisit: string
  nextAppointment: string
  provider: string
  complications: string[]
}

interface Appointment {
  id: string
  patientName: string
  date: string
  time: string
  type: string
  provider: string
  status: string
}

interface Alert {
  id: string
  patientName: string
  type: string
  message: string
  severity: string
  timestamp: string
}

export default function Dashboard() {
  const [patients, setPatients] = useState<Patient[]>([])
  const [appointments, setAppointments] = useState<Appointment[]>([])
  const [alerts, setAlerts] = useState<Alert[]>([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'patients' | 'appointments' | 'alerts'>('patients')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null)

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:5006/api/v1/patients').then(res => res.json()),
      fetch('http://localhost:5006/api/v1/appointments').then(res => res.json()),
      fetch('http://localhost:5006/api/v1/alerts').then(res => res.json())
    ])
      .then(([patientsData, appointmentsData, alertsData]) => {
        setPatients(patientsData.patients || [])
        setAppointments(appointmentsData.appointments || [])
        setAlerts(alertsData.alerts || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setLoading(false)
      })
  }, [])

  const filteredPatients = patients.filter(p =>
    p.name?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getRiskBadgeColor = (risk: string) => {
    switch(risk) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'moderate': return 'bg-yellow-100 text-yellow-800'
      default: return 'bg-green-100 text-green-800'
    }
  }

  const getSeverityColor = (severity: string) => {
    switch(severity) {
      case 'high': return 'border-l-4 border-red-500 bg-red-50'
      case 'medium': return 'border-l-4 border-yellow-500 bg-yellow-50'
      default: return 'border-l-4 border-blue-500 bg-blue-50'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-gradient-to-br from-pink-600 to-rose-600 p-2 rounded-lg">
              <Heart className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">MYNX NatalCare</div>
              <div className="text-xs text-gray-500">Dashboard</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('patients')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'patients'
                  ? 'bg-pink-50 text-pink-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Users className="h-5 w-5" />
              Patients
            </button>
            <button
              onClick={() => setActiveTab('appointments')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'appointments'
                  ? 'bg-pink-50 text-pink-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Calendar className="h-5 w-5" />
              Appointments
            </button>
            <button
              onClick={() => setActiveTab('alerts')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'alerts'
                  ? 'bg-pink-50 text-pink-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Bell className="h-5 w-5" />
              Alerts
              {alerts.length > 0 && (
                <span className="ml-auto bg-red-500 text-white text-xs px-2 py-0.5 rounded-full">
                  {alerts.length}
                </span>
              )}
            </button>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <Activity className="h-5 w-5" />
              Vital Signs
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <FileText className="h-5 w-5" />
              Reports
            </a>
          </div>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
            <Settings className="h-5 w-5" />
            Settings
          </a>
          <Link href="/" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
            <Home className="h-5 w-5" />
            Home
          </Link>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Maternal Care Dashboard</h1>
              <p className="text-sm text-gray-500">Monitor and manage prenatal care</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium">
                Schedule Visit
              </button>
              <button className="px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 font-medium">
                Add Patient
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Patients</div>
                <Users className="h-5 w-5 text-pink-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{patients.length}</div>
              <div className="text-xs text-green-600 mt-1">+8% this month</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">High Risk Cases</div>
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {patients.filter(p => p.riskLevel === 'high').length}
              </div>
              <div className="text-xs text-red-600 mt-1">Requires monitoring</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Today's Appointments</div>
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {appointments.filter(a => a.date === new Date().toISOString().split('T')[0]).length}
              </div>
              <div className="text-xs text-blue-600 mt-1">View schedule</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Alerts</div>
                <Bell className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{alerts.length}</div>
              <div className="text-xs text-yellow-600 mt-1">Review required</div>
            </div>
          </div>

          {/* Content Tabs */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="border-b border-gray-200 p-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder={`Search ${activeTab}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-pink-500 focus:border-pink-500"
                />
              </div>
            </div>

            {/* Patients Tab */}
            {activeTab === 'patients' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading patients...</div>
                ) : filteredPatients.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No patients found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Gestational Week</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Due Date</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Risk Level</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Provider</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Next Visit</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredPatients.map((patient) => (
                        <tr key={patient.id} className="hover:bg-gray-50">
                          <td className="px-6 py-4">
                            <div>
                              <div className="font-medium text-gray-900">{patient.name}</div>
                              <div className="text-sm text-gray-500">{patient.age} years • {patient.bloodType}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">Week {patient.gestationalWeek}</td>
                          <td className="px-6 py-4 text-sm text-gray-500">{patient.dueDate}</td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getRiskBadgeColor(patient.riskLevel)}`}>
                              {patient.riskLevel}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-900">{patient.provider}</td>
                          <td className="px-6 py-4 text-sm text-gray-500">{patient.nextAppointment}</td>
                          <td className="px-6 py-4">
                            <button
                              onClick={() => setSelectedPatient(patient)}
                              className="text-pink-600 hover:text-pink-800 text-sm font-medium"
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {/* Appointments Tab */}
            {activeTab === 'appointments' && (
              <div className="p-6">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading appointments...</div>
                ) : appointments.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No appointments scheduled</div>
                ) : (
                  <div className="space-y-3">
                    {appointments.map((apt) => (
                      <div key={apt.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3">
                              <div className="text-sm font-semibold text-gray-900">{apt.patientName}</div>
                              <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{apt.type}</span>
                            </div>
                            <div className="text-sm text-gray-500 mt-1">
                              {apt.date} at {apt.time} • {apt.provider}
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <button className="p-2 hover:bg-gray-100 rounded-lg">
                              <Phone className="h-4 w-4 text-gray-600" />
                            </button>
                            <button className="px-3 py-1 text-sm text-pink-600 hover:bg-pink-50 rounded-lg">
                              Reschedule
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Alerts Tab */}
            {activeTab === 'alerts' && (
              <div className="p-6">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading alerts...</div>
                ) : alerts.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No active alerts</div>
                ) : (
                  <div className="space-y-3">
                    {alerts.map((alert) => (
                      <div key={alert.id} className={`rounded-lg p-4 ${getSeverityColor(alert.severity)}`}>
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <AlertTriangle className="h-4 w-4" />
                              <span className="font-semibold text-sm">{alert.patientName}</span>
                              <span className="text-xs px-2 py-0.5 bg-white rounded-full">{alert.type}</span>
                            </div>
                            <div className="text-sm mb-2">{alert.message}</div>
                            <div className="text-xs text-gray-600">{alert.timestamp}</div>
                          </div>
                          <button className="px-3 py-1 text-sm bg-white hover:bg-gray-100 rounded-lg font-medium">
                            Review
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Patient Detail Modal */}
      {selectedPatient && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedPatient(null)}>
          <div className="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Patient Details</h2>
              <button onClick={() => setSelectedPatient(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedPatient.name}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Age</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedPatient.age} years</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Gestational Week</div>
                  <div className="text-lg font-semibold text-gray-900">Week {selectedPatient.gestationalWeek}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Due Date</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedPatient.dueDate}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Blood Type</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedPatient.bloodType}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Risk Level</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getRiskBadgeColor(selectedPatient.riskLevel)}`}>
                    {selectedPatient.riskLevel}
                  </span>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-2">Provider</div>
                <div className="text-lg font-semibold text-gray-900">{selectedPatient.provider}</div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-2">Complications</div>
                {selectedPatient.complications.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {selectedPatient.complications.map((comp, idx) => (
                      <span key={idx} className="px-3 py-1 bg-red-100 text-red-800 text-sm rounded-full">
                        {comp}
                      </span>
                    ))}
                  </div>
                ) : (
                  <div className="text-gray-500">None reported</div>
                )}
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-pink-600 text-white rounded-lg hover:bg-pink-700 font-medium">
                  Schedule Appointment
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  View Full Record
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

function X({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
    </svg>
  )
}
