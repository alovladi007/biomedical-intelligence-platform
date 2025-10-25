'use client';

import { useState, useEffect } from 'react';
import { predictionAPI } from '@/lib/api';

export default function PredictionHistory({ patientId }: { patientId?: number }) {
  const [predictions, setPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadPredictions();
  }, [patientId]);

  const loadPredictions = async () => {
    try {
      const response = patientId
        ? await predictionAPI.getByPatient(patientId)
        : await predictionAPI.list({ limit: 100 });
      setPredictions(response.data.predictions);
    } catch (err) {
      console.error('Failed to load predictions', err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'moderate': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">AI Prediction History</h2>

      {loading ? (
        <div className="text-center py-12">Loading...</div>
      ) : predictions.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No predictions found</div>
      ) : (
        <div className="space-y-4">
          {predictions.map(prediction => (
            <div key={prediction.id} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold">{prediction.model_name}</h3>
                  <p className="text-sm text-gray-600">v{prediction.model_version} • {prediction.prediction_type}</p>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskColor(prediction.risk_level)}`}>
                  {prediction.risk_level?.toUpperCase()}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-4">
                <div>
                  <p className="text-sm text-gray-600">Confidence Score</p>
                  <p className="text-2xl font-bold">{(prediction.confidence_score * 100).toFixed(1)}%</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Date</p>
                  <p className="font-medium">{new Date(prediction.created_at).toLocaleString()}</p>
                </div>
              </div>

              {prediction.recommendations && (
                <div className="mb-4">
                  <p className="text-sm font-medium text-gray-700 mb-2">Recommendations:</p>
                  <p className="text-sm text-gray-600">{prediction.recommendations}</p>
                </div>
              )}

              {prediction.reviewed_by_clinician && (
                <div className="bg-green-50 p-3 rounded-lg">
                  <p className="text-sm font-medium text-green-800">
                    ✓ Reviewed by clinician
                    {prediction.clinician_agreement ? ' (Agreement confirmed)' : ' (Disagreement noted)'}
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
