"""
EHR Provider Abstract Interface

This module defines the abstract interface that all EHR providers must implement.
This allows the system to seamlessly switch between different data sources
(mock JSON, FHIR servers, etc.) without changing the agent code.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class EHRProvider(ABC):
    """
    Abstract base class for EHR data providers.
    
    All providers must implement these methods to support:
    - Complete patient data retrieval
    - Structured queries (labs, medications, conditions)
    - RAG-based semantic search
    - Data summarization
    """
    
    @abstractmethod
    async def get_patient_json(self, patient_id: str) -> Dict[str, Any]:
        """
        Retrieve complete EHR data for a patient as a dictionary.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            Complete EHR data dictionary, or empty dict if not found
        """
        pass
    
    @abstractmethod
    async def get_summary(self, patient_id: str) -> str:
        """
        Get a human-readable summary of the patient's EHR.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            Multi-line text summary suitable for LLM context
        """
        pass
    
    @abstractmethod
    async def get_latest_lab(self, patient_id: str, lab_name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve the most recent lab result by name.
        
        Args:
            patient_id: Unique patient identifier
            lab_name: Lab test name (e.g., "HbA1c", "Blood Pressure")
            
        Returns:
            Lab result dictionary or None if not found
        """
        pass
    
    @abstractmethod
    async def get_all_labs(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all lab results for a patient.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            List of lab result dictionaries
        """
        pass
    
    @abstractmethod
    async def get_medications(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all active medications for a patient.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            List of medication dictionaries
        """
        pass
    
    @abstractmethod
    async def get_conditions(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        Retrieve all diagnosed conditions for a patient.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            List of condition dictionaries
        """
        pass
    
    @abstractmethod
    async def index_patient(self, patient_id: str) -> None:
        """
        Index the patient's EHR data for RAG search.
        This should be called before performing semantic searches.
        
        Args:
            patient_id: Unique patient identifier
        """
        pass
    
    @abstractmethod
    async def rag_search(
        self, 
        patient_id: str, 
        query: str, 
        k: int = 5,
        filter_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search over the patient's EHR data.
        
        Args:
            patient_id: Unique patient identifier
            query: Natural language query
            k: Number of results to return
            filter_type: Optional filter by data type
            
        Returns:
            List of search results with text, metadata, and relevance scores
        """
        pass
    
    @abstractmethod
    async def patient_exists(self, patient_id: str) -> bool:
        """
        Check if a patient exists in the data source.
        
        Args:
            patient_id: Unique patient identifier
            
        Returns:
            True if patient exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def list_patients(self) -> List[str]:
        """
        List all available patient IDs.
        
        Returns:
            List of patient IDs
        """
        pass

