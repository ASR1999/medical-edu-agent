import React, { useState, useEffect } from 'react';
import { FaUser, FaStethoscope, FaPills, FaFlask, FaSpinner } from 'react-icons/fa';

export default function EHRSidebar({ patientId, isOpen, onToggle }) {
  const [ehrData, setEhrData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (patientId && isOpen) {
      fetchEHRData();
    }
  }, [patientId, isOpen]);

  const fetchEHRData = async () => {
    setLoading(true);
    setError(null);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
      const response = await fetch(`${apiUrl}/ehr/${patientId}`);
      if (!response.ok) throw new Error('Failed to fetch EHR data');
      const data = await response.json();
      setEhrData(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed right-0 top-1/2 transform -translate-y-1/2 bg-blue-600 text-white px-2 py-6 rounded-l-lg shadow-lg hover:bg-blue-700 transition-colors z-50"
        title="Show Patient EHR"
      >
        <FaUser className="text-xl" />
      </button>
    );
  }

  return (
    <div className="w-80 bg-white border-l border-gray-200 shadow-lg overflow-y-auto">
      {/* Header */}
      <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-blue-700 text-white p-4 flex justify-between items-center">
        <h2 className="text-lg font-bold flex items-center">
          <FaUser className="mr-2" />
          Patient EHR
        </h2>
        <button
          onClick={onToggle}
          className="text-white hover:bg-blue-800 p-1 rounded"
          title="Hide sidebar"
        >
          ✕
        </button>
      </div>

      {/* Content */}
      <div className="p-4 space-y-4">
        {loading && (
          <div className="flex items-center justify-center py-8">
            <FaSpinner className="animate-spin text-blue-600 text-3xl" />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}

        {ehrData && !loading && (
          <>
            {/* Personal Info */}
            <div className="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                <FaUser className="mr-2 text-blue-600" />
                Demographics
              </h3>
              <div className="text-sm space-y-1">
                <p><strong>Name:</strong> {ehrData.personal_info?.name}</p>
                <p><strong>Age:</strong> {ehrData.personal_info?.age} years</p>
                <p><strong>Gender:</strong> {ehrData.personal_info?.gender}</p>
              </div>
            </div>

            {/* Conditions */}
            {ehrData.conditions && ehrData.conditions.length > 0 && (
              <div className="bg-red-50 rounded-lg p-3 border border-red-200">
                <h3 className="font-semibold text-red-900 mb-2 flex items-center">
                  <FaStethoscope className="mr-2 text-red-600" />
                  Conditions
                </h3>
                <ul className="text-sm space-y-1">
                  {ehrData.conditions.map((condition, idx) => (
                    <li key={idx} className="text-red-800">
                      • {condition.name}
                      <span className="text-xs text-red-600 ml-1">
                        (since {condition.diagnosed_on})
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Medications */}
            {ehrData.medications && ehrData.medications.length > 0 && (
              <div className="bg-green-50 rounded-lg p-3 border border-green-200">
                <h3 className="font-semibold text-green-900 mb-2 flex items-center">
                  <FaPills className="mr-2 text-green-600" />
                  Medications
                </h3>
                <ul className="text-sm space-y-1">
                  {ehrData.medications.map((med, idx) => (
                    <li key={idx} className="text-green-800">
                      • <strong>{med.name}</strong> {med.dosage}
                      <br />
                      <span className="text-xs text-green-600 ml-3">
                        {med.frequency}
                      </span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Recent Labs */}
            {ehrData.recent_labs && ehrData.recent_labs.length > 0 && (
              <div className="bg-purple-50 rounded-lg p-3 border border-purple-200">
                <h3 className="font-semibold text-purple-900 mb-2 flex items-center">
                  <FaFlask className="mr-2 text-purple-600" />
                  Recent Labs
                </h3>
                <div className="text-sm space-y-2">
                  {ehrData.recent_labs.slice(0, 5).map((lab, idx) => (
                    <div key={idx} className="text-purple-800">
                      <p className="font-medium">{lab.test_name}</p>
                      <p className="text-purple-700">
                        <strong>{lab.value}</strong> ({lab.date})
                      </p>
                      {lab.notes && (
                        <p className="text-xs text-purple-600 mt-1">{lab.notes}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Doctor's Notes */}
            {ehrData.doctor_notes && (
              <div className="bg-yellow-50 rounded-lg p-3 border border-yellow-200">
                <h3 className="font-semibold text-yellow-900 mb-2">
                  📝 Doctor's Notes
                </h3>
                <p className="text-sm text-yellow-800 leading-relaxed">
                  {ehrData.doctor_notes}
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}



