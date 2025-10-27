"""
EHR Service (Legacy Compatibility Layer)

This module provides backward compatibility with the original EHR service interface
while delegating to the new provider-based architecture.
"""

from app.services.ehr_provider_factory import get_ehr_provider


class EHRService:
    """
    Legacy EHR service that delegates to the provider factory.
    Maintained for backward compatibility.
    """
    
    def __init__(self):
        self.provider = get_ehr_provider()
    
    def get_patient_json(self, patient_id: str) -> dict:
        """Get complete patient EHR data"""
        return self.provider.get_patient_json(patient_id)
    
    def get_patient_data(self, patient_id: str) -> str:
        """Get human-readable summary"""
        return self.provider.get_summary(patient_id)


# Singleton instance (legacy)
ehr_service = EHRService()
