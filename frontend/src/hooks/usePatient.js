import { useState, useEffect, useCallback } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export function usePatient(initialPatientId = 'patient_id_12345') {
  const [patientId, setPatientId] = useState(initialPatientId);
  const [patientData, setPatientData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPatientData = useCallback(async (id) => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/ehr/${id}`);
      if (!response.ok) {
        throw new Error(`Failed to fetch patient data: ${response.statusText}`);
      }
      const data = await response.json();
      setPatientData(data.data);
    } catch (err) {
      console.error('Error fetching patient data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const switchPatient = useCallback((newPatientId) => {
    setPatientId(newPatientId);
    fetchPatientData(newPatientId);
  }, [fetchPatientData]);

  // Fetch on mount and when patient changes
  useEffect(() => {
    fetchPatientData(patientId);
  }, [patientId, fetchPatientData]);

  return {
    patientId,
    patientData,
    loading,
    error,
    switchPatient,
    refreshPatientData: () => fetchPatientData(patientId)
  };
}

