import React from 'react';

const MOCK_PATIENTS = [
  {
    id: 'patient_id_12345',
    name: 'Jane Doe',
    age: 42,
    gender: 'Female',
    primaryCondition: 'Type 2 Diabetes, Hypertension'
  },
  {
    id: 'patient_id_67890',
    name: 'John Smith',
    age: 58,
    gender: 'Male',
    primaryCondition: 'Coronary Artery Disease'
  },
  {
    id: 'patient_id_24680',
    name: 'Maria Garcia',
    age: 35,
    gender: 'Female',
    primaryCondition: 'Asthma'
  },
  {
    id: 'patient_id_13579',
    name: 'Robert Johnson',
    age: 67,
    gender: 'Male',
    primaryCondition: 'Osteoarthritis'
  },
  {
    id: 'patient_id_98765',
    name: 'Sarah Chen',
    age: 29,
    gender: 'Female',
    primaryCondition: 'PCOS, Hypothyroidism'
  }
];

export default function PatientSelector({ selectedPatientId, onPatientChange }) {
  const selectedPatient = MOCK_PATIENTS.find(p => p.id === selectedPatientId) || MOCK_PATIENTS[0];

  return (
    <div className="relative">
      <label htmlFor="patient-select" className="block text-sm font-medium text-gray-700 mb-1">
        👤 Active Patient
      </label>
      <select
        id="patient-select"
        value={selectedPatientId}
        onChange={(e) => onPatientChange(e.target.value)}
        className="block w-full px-4 py-2 pr-8 border border-gray-300 rounded-lg bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
      >
        {MOCK_PATIENTS.map((patient) => (
          <option key={patient.id} value={patient.id}>
            {patient.name} ({patient.age}{patient.gender[0]}) - {patient.primaryCondition}
          </option>
        ))}
      </select>
      <div className="mt-2 text-xs text-gray-600 bg-blue-50 p-2 rounded border border-blue-100">
        <strong>Current:</strong> {selectedPatient.name}, {selectedPatient.age} year old {selectedPatient.gender.toLowerCase()}
      </div>
    </div>
  );
}

export { MOCK_PATIENTS };



