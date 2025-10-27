"""
FHIR EHR Provider

This provider connects to a FHIR-compliant server (e.g., HAPI FHIR) to retrieve
real EHR data. It translates FHIR resources into the standardized format expected
by the AI agent.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .ehr_provider import EHRProvider
from .rag_index import get_rag_index
from . import fhir_client
from .fhir_client import FHIRClientError

logger = logging.getLogger(__name__)


class FHIRProvider(EHRProvider):
    """
    FHIR-based EHR provider that fetches data from a FHIR server.
    
    Features:
    - Real-time data from FHIR-compliant systems
    - Standard FHIR resource mapping
    - Full RAG support for semantic search
    - Graceful error handling with fallbacks
    """
    
    def __init__(self):
        """Initialize the FHIR provider"""
        self.rag = get_rag_index()
        self._test_connection()
        logger.info("FHIR EHR Provider initialized")
    
    def _test_connection(self):
        """Test FHIR server connectivity on initialization"""
        try:
            if fhir_client.test_connection():
                logger.info("FHIR server connection verified")
            else:
                logger.warning("FHIR server connection failed - provider may not work correctly")
        except Exception as e:
            logger.error(f"Error testing FHIR connection: {e}")
    
    def _fhir_to_simple_format(self, patient_id: str) -> Dict[str, Any]:
        """
        Fetch FHIR resources and convert to simplified format compatible with mock provider.
        
        This creates a unified data structure regardless of source.
        """
        try:
            # Fetch all relevant FHIR resources
            patient = fhir_client.get_patient(patient_id)
            observations = fhir_client.search_observations(patient_id)
            conditions = fhir_client.search_conditions(patient_id)
            medications = fhir_client.search_medications(patient_id)
            procedures = fhir_client.search_procedures(patient_id)
            
            # Convert to simplified format
            name = fhir_client.extract_patient_name(patient)
            birth_date = patient.get("birthDate", "Unknown")
            gender = patient.get("gender", "Unknown").capitalize()
            
            # Calculate age from birth date
            try:
                birth = datetime.fromisoformat(birth_date)
                age = (datetime.now() - birth).days // 365
            except:
                age = "Unknown"
            
            # Convert conditions
            simple_conditions = []
            for cond in conditions:
                code = cond.get("code", {})
                simple_conditions.append({
                    "name": fhir_client.extract_code_display(code),
                    "diagnosed_on": cond.get("onsetDateTime", "Unknown")[:10]  # ISO date
                })
            
            # Convert medications
            simple_medications = []
            for med_stmt in medications:
                med_ref = med_stmt.get("medicationCodeableConcept", {})
                dosage = med_stmt.get("dosage", [{}])[0]
                simple_medications.append({
                    "name": fhir_client.extract_code_display(med_ref),
                    "dosage": dosage.get("text", "As directed"),
                    "frequency": dosage.get("timing", {}).get("code", {}).get("text", "As prescribed")
                })
            
            # Convert observations to labs
            simple_labs = []
            for obs in observations[:10]:  # Limit to 10 most recent
                code = obs.get("code", {})
                test_name = fhir_client.extract_code_display(code)
                value = fhir_client.extract_observation_value(obs)
                date = obs.get("effectiveDateTime", "Unknown")[:10]
                
                # Extract notes from interpretation or note
                notes = ""
                interpretation = obs.get("interpretation", [])
                if interpretation:
                    notes = fhir_client.extract_code_display(interpretation[0])
                
                simple_labs.append({
                    "test_name": test_name,
                    "value": value,
                    "date": date,
                    "notes": notes
                })
            
            # Aggregate doctor notes from various sources
            doctor_notes_parts = []
            for proc in procedures[:3]:  # Last 3 procedures
                code = proc.get("code", {})
                date = proc.get("performedDateTime", "Unknown")[:10]
                proc_name = fhir_client.extract_code_display(code)
                doctor_notes_parts.append(f"Procedure on {date}: {proc_name}")
            
            doctor_notes = " | ".join(doctor_notes_parts) if doctor_notes_parts else "No recent procedures."
            
            # Assemble simplified structure
            return {
                "personal_info": {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "birth_date": birth_date
                },
                "conditions": simple_conditions,
                "medications": simple_medications,
                "recent_labs": simple_labs,
                "doctor_notes": doctor_notes,
                "_source": "fhir",
                "_patient_resource": patient  # Keep original for reference
            }
            
        except FHIRClientError as e:
            logger.error(f"FHIR error fetching patient {patient_id}: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error fetching patient {patient_id}: {e}")
            return {}
    
    def get_patient_json(self, patient_id: str) -> Dict[str, Any]:
        """Get complete patient EHR data from FHIR"""
        return self._fhir_to_simple_format(patient_id)
    
    def get_summary(self, patient_id: str) -> str:
        """Generate a human-readable summary from FHIR data"""
        data = self.get_patient_json(patient_id)
        if not data:
            return f"Error: Patient ID '{patient_id}' not found or FHIR server unavailable."
        
        # Reuse the same summary format as mock provider for consistency
        personal = data.get('personal_info', {})
        name = personal.get('name', 'Unknown')
        age = personal.get('age', 'Unknown')
        gender = personal.get('gender', 'Unknown')
        
        conditions = data.get('conditions', [])
        condition_names = ", ".join([c.get('name', 'Unknown') for c in conditions]) if conditions else "None"
        
        medications = data.get('medications', [])
        med_summary = []
        for med in medications:
            med_name = med.get('name', 'Unknown')
            dosage = med.get('dosage', '')
            frequency = med.get('frequency', '')
            med_summary.append(f"{med_name} {dosage} {frequency}".strip())
        meds_str = ", ".join(med_summary) if med_summary else "None"
        
        lines = [
            f"=== EHR Summary for {name} (FHIR) ===",
            f"Demographics: {age} years old, {gender}",
            f"",
            f"Active Conditions: {condition_names}",
            f"",
            f"Current Medications: {meds_str}",
            f"",
            f"Recent Lab Results:"
        ]
        
        labs = data.get('recent_labs', [])
        if labs:
            for lab in labs:
                test_name = lab.get('test_name', 'Unknown')
                value = lab.get('value', 'N/A')
                date = lab.get('date', 'Unknown')
                notes = lab.get('notes', '')
                lines.append(f"  • {test_name}: {value} (Date: {date})")
                if notes:
                    lines.append(f"    Notes: {notes}")
        else:
            lines.append("  No recent labs recorded.")
        
        doctor_notes = data.get('doctor_notes', '')
        if doctor_notes:
            lines.append(f"")
            lines.append(f"Recent Procedures: {doctor_notes}")
        
        lines.append(f"")
        lines.append(f"[Data Source: FHIR Server]")
        
        return "\n".join(lines)
    
    def get_latest_lab(self, patient_id: str, lab_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent lab result by name"""
        data = self.get_patient_json(patient_id)
        labs = data.get('recent_labs', [])
        
        # Find matching lab (case-insensitive)
        for lab in labs:
            if lab.get('test_name', '').lower() == lab_name.lower():
                return lab
        
        return None
    
    def get_all_labs(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all lab results"""
        data = self.get_patient_json(patient_id)
        return data.get('recent_labs', [])
    
    def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all medications"""
        data = self.get_patient_json(patient_id)
        return data.get('medications', [])
    
    def get_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all conditions"""
        data = self.get_patient_json(patient_id)
        return data.get('conditions', [])
    
    def index_patient(self, patient_id: str) -> None:
        """Index patient data for RAG search"""
        data = self.get_patient_json(patient_id)
        if data:
            self.rag.index_patient(patient_id, data)
            logger.info(f"Indexed FHIR patient {patient_id} for RAG search")
        else:
            logger.warning(f"Cannot index patient {patient_id}: FHIR data not available")
    
    def rag_search(
        self, 
        patient_id: str, 
        query: str, 
        k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search over patient EHR"""
        return self.rag.search(patient_id, query, k=k, filter_type=filter_type)
    
    def patient_exists(self, patient_id: str) -> bool:
        """Check if patient exists in FHIR server"""
        try:
            patient = fhir_client.get_patient(patient_id)
            return bool(patient)
        except FHIRClientError:
            return False
        except Exception:
            return False
    
    def list_patients(self) -> List[str]:
        """
        List all patient IDs (limited implementation).
        Note: FHIR servers may have thousands of patients, so this returns empty.
        In production, use search with specific criteria.
        """
        logger.warning("list_patients() not fully implemented for FHIR - use search instead")
        return []

