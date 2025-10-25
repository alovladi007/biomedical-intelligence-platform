'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { Activity, Wifi, Battery, AlertTriangle, Home, BarChart3, Settings, Search, CheckCircle, XCircle, TrendingUp, Thermometer } from 'lucide-react'

interface Device {
  id: string
  deviceName: string
  deviceType: string
  patientId: string
  patientName: string
  status: string
  battery: number
  lastReading: {
    timestamp: string
    value: number
    unit: string
    type: string
  }
  alerts: number
  location: string
}

interface SensorReading {
  id: string
  deviceId: string
  deviceName: string
  type: string
  value: number
  unit: string
  timestamp: string
  status: string
}

export default function Dashboard() {
  const [devices, setDevices] = useState<Device[]>([])
  const [readings, setReadings] = useState<SensorReading[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState<'devices' | 'readings'>('devices')

  useEffect(() => {
    Promise.all([
      fetch('http://localhost:5003/api/v1/devices').then(res => res.json()),
      fetch('http://localhost:5003/api/v1/readings').then(res => res.json())
    ])
      .then(([devicesData, readingsData]) => {
        setDevices(devicesData.devices || [])
        setReadings(readingsData.readings || [])
        setLoading(false)
      })
      .catch(err => {
        console.error('Error fetching data:', err)
        setLoading(false)
      })
  }, [])

  const filteredDevices = devices.filter(d =>
    d.deviceName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.patientName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    d.deviceType.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getStatusBadge = (status: string) => {
    switch(status) {
      case 'active': return <div className="flex items-center gap-1"><CheckCircle className="h-4 w-4 text-green-600" /><span className="text-green-600">Active</span></div>
      case 'warning': return <div className="flex items-center gap-1"><AlertTriangle className="h-4 w-4 text-yellow-600" /><span className="text-yellow-600">Warning</span></div>
      case 'offline': return <div className="flex items-center gap-1"><XCircle className="h-4 w-4 text-red-600" /><span className="text-red-600">Offline</span></div>
      default: return <span className="text-gray-600">Unknown</span>
    }
  }

  const getBatteryColor = (level: number) => {
    if (level >= 60) return 'text-green-600'
    if (level >= 30) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getDeviceTypeColor = (type: string) => {
    switch(type) {
      case 'Heart Monitor': return 'bg-red-100 text-red-800'
      case 'Glucose Monitor': return 'bg-blue-100 text-blue-800'
      case 'Blood Pressure': return 'bg-purple-100 text-purple-800'
      case 'Temperature': return 'bg-orange-100 text-orange-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <Link href="/" className="flex items-center gap-2">
            <div className="bg-green-600 p-2 rounded-lg">
              <Activity className="h-6 w-6 text-white" />
            </div>
            <div>
              <div className="font-bold text-gray-900">Biosensing</div>
              <div className="text-xs text-gray-500">Real-time Monitoring</div>
            </div>
          </Link>
        </div>

        <nav className="flex-1 p-4">
          <div className="space-y-1">
            <button
              onClick={() => setActiveTab('devices')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'devices'
                  ? 'bg-green-50 text-green-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Wifi className="h-5 w-5" />
              Devices
            </button>
            <button
              onClick={() => setActiveTab('readings')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium ${
                activeTab === 'readings'
                  ? 'bg-green-50 text-green-600'
                  : 'text-gray-700 hover:bg-gray-50'
              }`}
            >
              <Activity className="h-5 w-5" />
              Readings
            </button>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <AlertTriangle className="h-5 w-5" />
              Alerts
            </a>
            <a href="#" className="flex items-center gap-3 px-4 py-3 text-gray-700 hover:bg-gray-50 rounded-lg">
              <BarChart3 className="h-5 w-5" />
              Analytics
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
              <h1 className="text-2xl font-bold text-gray-900">Biosensing Dashboard</h1>
              <p className="text-sm text-gray-500">Monitor devices and sensor readings in real-time</p>
            </div>
            <div className="flex items-center gap-4">
              <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium">
                Add Device
              </button>
            </div>
          </div>
        </header>

        {/* Stats */}
        <div className="p-8 overflow-y-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Total Devices</div>
                <Wifi className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{devices.length}</div>
              <div className="text-xs text-green-600 mt-1">+5 new this week</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Devices</div>
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {devices.filter(d => d.status === 'active').length}
              </div>
              <div className="text-xs text-green-600 mt-1">Operating normally</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Active Alerts</div>
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {devices.reduce((acc, d) => acc + d.alerts, 0)}
              </div>
              <div className="text-xs text-yellow-600 mt-1">Requires attention</div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-2">
                <div className="text-sm font-medium text-gray-500">Readings Today</div>
                <Activity className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-2xl font-bold text-gray-900">{readings.length}</div>
              <div className="text-xs text-blue-600 mt-1">Real-time data</div>
            </div>
          </div>

          {/* Content */}
          <div className="bg-white rounded-lg border border-gray-200">
            <div className="p-4 border-b border-gray-200">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  type="text"
                  placeholder={`Search ${activeTab}...`}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
              </div>
            </div>

            {/* Devices Tab */}
            {activeTab === 'devices' && (
              <div className="overflow-x-auto">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading devices...</div>
                ) : filteredDevices.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No devices found</div>
                ) : (
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Device</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Patient</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Battery</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Last Reading</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Alerts</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {filteredDevices.map((device) => (
                        <tr key={device.id} className="hover:bg-gray-50 cursor-pointer" onClick={() => setSelectedDevice(device)}>
                          <td className="px-6 py-4">
                            <div>
                              <div className="font-medium text-gray-900">{device.deviceName}</div>
                              <div className="text-sm text-gray-500">{device.id}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDeviceTypeColor(device.deviceType)}`}>
                              {device.deviceType}
                            </span>
                          </td>
                          <td className="px-6 py-4">
                            <div>
                              <div className="text-sm font-medium text-gray-900">{device.patientName}</div>
                              <div className="text-sm text-gray-500">{device.patientId}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-sm">
                            {getStatusBadge(device.status)}
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-2">
                              <Battery className={`h-4 w-4 ${getBatteryColor(device.battery)}`} />
                              <span className={`text-sm font-medium ${getBatteryColor(device.battery)}`}>
                                {device.battery}%
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            <div>
                              <div className="text-sm font-medium text-gray-900">
                                {device.lastReading.value} {device.lastReading.unit}
                              </div>
                              <div className="text-xs text-gray-500">{device.lastReading.timestamp}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            {device.alerts > 0 ? (
                              <span className="inline-flex px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800">
                                {device.alerts} Alert{device.alerts > 1 ? 's' : ''}
                              </span>
                            ) : (
                              <span className="text-sm text-gray-400">None</span>
                            )}
                          </td>
                          <td className="px-6 py-4">
                            <button className="text-green-600 hover:text-green-800 text-sm font-medium">
                              View
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}

            {/* Readings Tab */}
            {activeTab === 'readings' && (
              <div className="p-6">
                {loading ? (
                  <div className="p-12 text-center text-gray-500">Loading readings...</div>
                ) : readings.length === 0 ? (
                  <div className="p-12 text-center text-gray-500">No readings available</div>
                ) : (
                  <div className="space-y-3">
                    {readings.map((reading) => (
                      <div key={reading.id} className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <Thermometer className="h-5 w-5 text-green-600" />
                              <span className="font-semibold text-gray-900">{reading.deviceName}</span>
                              <span className="text-xs px-2 py-1 bg-blue-100 text-blue-800 rounded-full">{reading.type}</span>
                            </div>
                            <div className="grid grid-cols-3 gap-4 text-sm">
                              <div>
                                <span className="text-gray-500">Value:</span>
                                <span className="ml-2 font-medium text-gray-900">{reading.value} {reading.unit}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Status:</span>
                                <span className="ml-2 font-medium text-gray-900 capitalize">{reading.status}</span>
                              </div>
                              <div>
                                <span className="text-gray-500">Time:</span>
                                <span className="ml-2 font-medium text-gray-900">{reading.timestamp}</span>
                              </div>
                            </div>
                          </div>
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

      {/* Device Detail Modal */}
      {selectedDevice && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedDevice(null)}>
          <div className="bg-white rounded-lg max-w-3xl w-full p-6 max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Device Details</h2>
              <button onClick={() => setSelectedDevice(null)} className="text-gray-400 hover:text-gray-600">
                <X className="h-6 w-6" />
              </button>
            </div>

            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm font-medium text-gray-500">Device Name</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDevice.deviceName}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Device ID</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDevice.id}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Type</div>
                  <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${getDeviceTypeColor(selectedDevice.deviceType)}`}>
                    {selectedDevice.deviceType}
                  </span>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Status</div>
                  <div className="mt-1">{getStatusBadge(selectedDevice.status)}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Patient</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDevice.patientName}</div>
                  <div className="text-sm text-gray-500">{selectedDevice.patientId}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-gray-500">Location</div>
                  <div className="text-lg font-semibold text-gray-900">{selectedDevice.location}</div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Battery Level</div>
                    <div className="flex items-center gap-2">
                      <Battery className={`h-6 w-6 ${getBatteryColor(selectedDevice.battery)}`} />
                      <span className={`text-2xl font-bold ${getBatteryColor(selectedDevice.battery)}`}>
                        {selectedDevice.battery}%
                      </span>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-gray-500 mb-2">Active Alerts</div>
                    <div className="text-2xl font-bold text-gray-900">{selectedDevice.alerts}</div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200">
                <div className="text-sm font-medium text-gray-500 mb-3">Last Reading</div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-green-700">Type</div>
                      <div className="text-lg font-semibold text-green-900">{selectedDevice.lastReading.type}</div>
                    </div>
                    <div>
                      <div className="text-sm text-green-700">Value</div>
                      <div className="text-lg font-semibold text-green-900">
                        {selectedDevice.lastReading.value} {selectedDevice.lastReading.unit}
                      </div>
                    </div>
                    <div className="col-span-2">
                      <div className="text-sm text-green-700">Timestamp</div>
                      <div className="text-lg font-semibold text-green-900">{selectedDevice.lastReading.timestamp}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-gray-200 flex gap-3">
                <button className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-medium">
                  View History
                </button>
                <button className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium">
                  Configure Device
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
