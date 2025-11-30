"""
Mock EHR Provider

This provider reads from local JSON files for development and demonstration.
It supports the full EHR provider interface including RAG search.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from .ehr_provider import EHRProvider
from .rag_index import get_rag_index

logger = logging.getLogger(__name__)

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/mock_ehr.json")


class MockEHRProvider(EHRProvider):
    """
    Mock EHR provider that reads from a local JSON file.
    
    Features:
    - Fast local access
    - Full RAG support
    - Easy testing and development
    - Realistic data structure
    """
    
    def __init__(self):
        """Initialize the mock provider by loading the JSON database"""
        self.rag = get_rag_index()
        self.db = {}
        self._load_database()
        logger.info(f"Mock EHR Provider initialized with {len(self.db)} patients")
    
    def _load_database(self):
        """Load the mock EHR database from JSON"""
        try:
            if os.path.exists(DB_PATH):
                with open(DB_PATH, 'r') as f:
                    self.db = json.load(f)
                logger.info(f"Loaded mock EHR database from {DB_PATH}")
            else:
                logger.warning(f"Mock EHR database not found at {DB_PATH}")
                self.db = {}
        except Exception as e:
            logger.error(f"Error loading mock EHR database: {e}")
            self.db = {}
    
    def reload_database(self):
        """Reload the database from disk (useful for development)"""
        self._load_database()
    
    async def get_patient_json(self, patient_id: str) -> Dict[str, Any]:
        """Get complete patient EHR data"""
        return self.db.get(patient_id, {})
    
    async def get_summary(self, patient_id: str) -> str:
        """Generate a human-readable summary"""
        data = await self.get_patient_json(patient_id)
        if not data:
            return f"Error: Patient ID '{patient_id}' not found in mock database."
        
        # Extract key information
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
        
        # Build summary
        lines = [
            f"=== EHR Summary for {name} ===",
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
                date = lab.get('date', 'Unknown date')
                notes = lab.get('notes', '')
                lines.append(f"  • {test_name}: {value} (Date: {date})")
                if notes:
                    lines.append(f"    Notes: {notes}")
        else:
            lines.append("  No recent labs recorded.")
        
        doctor_notes = data.get('doctor_notes', '')
        if doctor_notes:
            lines.append(f"")
            lines.append(f"Doctor's Notes: {doctor_notes}")
        
        return "\n".join(lines)
    
    async def get_latest_lab(self, patient_id: str, lab_name: str) -> Optional[Dict[str, Any]]:
        """Get the most recent lab result by name"""
        data = await self.get_patient_json(patient_id)
        labs = data.get('recent_labs', [])
        
        # Find labs matching the name (case-insensitive)
        matching_labs = [
            lab for lab in labs 
            if lab.get('test_name', '').lower() == lab_name.lower()
        ]
        
        if not matching_labs:
            return None
        
        # Sort by date (most recent first) and return the first
        def parse_date(date_str):
            try:
                return datetime.fromisoformat(date_str)
            except ValueError:
                # Handle non-ISO formats if necessary, or return min date
                return datetime.min

        try:
            sorted_labs = sorted(
                matching_labs, 
                key=lambda x: parse_date(x.get('date', '1970-01-01')),
                reverse=True
            )
            return sorted_labs[0]
        except Exception as e:
            logger.error(f"Error sorting labs for {patient_id}: {e}")
            # If sorting fails, return the first match as fallback
            return matching_labs[0]
    
    async def get_all_labs(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all lab results"""
        data = await self.get_patient_json(patient_id)
        return data.get('recent_labs', [])
    
    async def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all medications"""
        data = await self.get_patient_json(patient_id)
        return data.get('medications', [])
    
    async def get_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get all conditions"""
        data = await self.get_patient_json(patient_id)
        return data.get('conditions', [])
    
    async def index_patient(self, patient_id: str) -> None:
        """Index patient data for RAG search"""
        data = await self.get_patient_json(patient_id)
        if data:
            self.rag.index_patient(patient_id, data)
            logger.info(f"Indexed patient {patient_id} for RAG search")
        else:
            logger.warning(f"Cannot index patient {patient_id}: data not found")
    
    async def rag_search(
        self, 
        patient_id: str, 
        query: str, 
        k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Perform semantic search over patient EHR"""
        return self.rag.search(patient_id, query, k=k, filter_type=filter_type)
    
    async def patient_exists(self, patient_id: str) -> bool:
        """Check if patient exists"""
        return patient_id in self.db
    
    async def list_patients(self) -> List[str]:
        """List all patient IDs"""
        return list(self.db.keys())
    
    def add_patient(self, patient_id: str, data: Dict[str, Any]) -> None:
        """
        Add or update a patient in the mock database (in-memory only).
        For persistence, the JSON file would need to be written.
        
        Args:
            patient_id: Patient identifier
            data: Complete EHR data dictionary
        """
        self.db[patient_id] = data
        logger.info(f"Added/updated patient {patient_id} in mock database (in-memory)")
    
    def save_database(self) -> bool:
        """
        Save the current database to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(DB_PATH, 'w') as f:
                json.dump(self.db, f, indent=2)
            logger.info(f"Saved mock EHR database to {DB_PATH}")
            return True
        except Exception as e:
            logger.error(f"Error saving mock EHR database: {e}")
            return False

