'use client';

import { useState, useEffect } from 'react';
import { patientAPI } from '@/lib/api';
import Link from 'next/link';

export default function PatientList() {
  const [patients, setPatients] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    try {
      const response = await patientAPI.list({ limit: 100 });
      setPatients(response.data.patients);
    } catch (err) {
      console.error('Failed to load patients', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredPatients = patients.filter(p =>
    p.first_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.last_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.mrn.includes(searchTerm)
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Patients</h1>
        <Link
          href="/dashboard/patients/new"
          className="bg-indigo-600 text-white px-6 py-2 rounded-lg hover:bg-indigo-700"
        >
          + Add Patient
        </Link>
      </div>

      <div className="mb-6">
        <input
          type="text"
          placeholder="Search by name or MRN..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg"
        />
      </div>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">MRN</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Name</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">DOB</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Sex</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredPatients.map(patient => (
                <tr key={patient.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap font-mono text-sm">{patient.mrn}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{patient.first_name} {patient.last_name}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{new Date(patient.date_of_birth).toLocaleDateString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap">{patient.sex}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Link
                      href={`/dashboard/patients/${patient.id}`}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
