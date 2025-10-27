"""
FHIR Client for HAPI FHIR Server Integration

This module provides functions to interact with a FHIR-compliant server (e.g., HAPI FHIR).
It handles authentication, request formatting, and error handling for FHIR resources.

FHIR Resources Supported:
- Patient: Demographics and identification
- Observation: Lab results, vitals, measurements
- Condition: Diagnoses and health problems
- MedicationStatement: Current and past medications
- Procedure: Surgical and medical procedures
- DiagnosticReport: Lab reports and imaging results
"""

import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import FHIR_BASE_URL, FHIR_BEARER_TOKEN, FHIR_TIMEOUT

logger = logging.getLogger(__name__)


class FHIRClientError(Exception):
    """Custom exception for FHIR client errors"""
    pass


def _get_headers() -> Dict[str, str]:
    """Generate headers for FHIR requests"""
    headers = {
        "Accept": "application/fhir+json",
        "Content-Type": "application/fhir+json"
    }
    if FHIR_BEARER_TOKEN:
        headers["Authorization"] = f"Bearer {FHIR_BEARER_TOKEN}"
    return headers


def _make_request(method: str, url: str, **kwargs) -> Dict[str, Any]:
    """
    Make a FHIR request with error handling.
    
    Args:
        method: HTTP method (GET, POST, etc.)
        url: Full URL
        **kwargs: Additional arguments for requests
        
    Returns:
        Parsed JSON response
        
    Raises:
        FHIRClientError: If request fails
    """
    try:
        response = requests.request(
            method,
            url,
            headers=_get_headers(),
            timeout=FHIR_TIMEOUT,
            **kwargs
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error(f"FHIR request timeout: {url}")
        raise FHIRClientError(f"Request timeout for {url}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"FHIR HTTP error: {e.response.status_code} - {e.response.text}")
        raise FHIRClientError(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
    except requests.exceptions.RequestException as e:
        logger.error(f"FHIR request error: {e}")
        raise FHIRClientError(f"Request failed: {str(e)}")
    except ValueError as e:
        logger.error(f"FHIR JSON parsing error: {e}")
        raise FHIRClientError(f"Invalid JSON response: {str(e)}")


# ==================== Patient ====================

def get_patient(patient_id: str) -> Dict[str, Any]:
    """
    Retrieve a Patient resource by ID.
    
    Args:
        patient_id: FHIR Patient resource ID
        
    Returns:
        Patient resource dictionary
    """
    url = f"{FHIR_BASE_URL}/Patient/{patient_id}"
    logger.info(f"Fetching Patient: {patient_id}")
    return _make_request("GET", url)


def search_patients(name: Optional[str] = None, identifier: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search for patients by name or identifier.
    
    Args:
        name: Patient name (family or given)
        identifier: Patient identifier
        
    Returns:
        List of Patient resources
    """
    url = f"{FHIR_BASE_URL}/Patient"
    params = {}
    if name:
        params["name"] = name
    if identifier:
        params["identifier"] = identifier
    
    logger.info(f"Searching Patients with params: {params}")
    response = _make_request("GET", url, params=params)
    return [entry["resource"] for entry in response.get("entry", [])]


# ==================== Observation ====================

def search_observations(
    patient_id: str,
    category: Optional[str] = None,
    code: Optional[str] = None,
    date_from: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for Observation resources (labs, vitals, etc.).
    
    Args:
        patient_id: Patient ID
        category: Observation category (e.g., "laboratory", "vital-signs")
        code: LOINC or SNOMED code
        date_from: Filter observations from this date (ISO format)
        
    Returns:
        List of Observation resources
    """
    url = f"{FHIR_BASE_URL}/Observation"
    params = {"patient": patient_id, "_sort": "-date"}
    
    if category:
        params["category"] = category
    if code:
        params["code"] = code
    if date_from:
        params["date"] = f"ge{date_from}"
    
    logger.info(f"Searching Observations for patient {patient_id}")
    response = _make_request("GET", url, params=params)
    return [entry["resource"] for entry in response.get("entry", [])]


def get_latest_observation(patient_id: str, code: str) -> Optional[Dict[str, Any]]:
    """
    Get the most recent observation by code.
    
    Args:
        patient_id: Patient ID
        code: LOINC code (e.g., "4548-4" for HbA1c)
        
    Returns:
        Most recent Observation resource or None
    """
    observations = search_observations(patient_id, code=code)
    return observations[0] if observations else None


# ==================== Condition ====================

def search_conditions(
    patient_id: str,
    clinical_status: Optional[str] = "active"
) -> List[Dict[str, Any]]:
    """
    Search for Condition resources (diagnoses).
    
    Args:
        patient_id: Patient ID
        clinical_status: Filter by status ("active", "inactive", "resolved")
        
    Returns:
        List of Condition resources
    """
    url = f"{FHIR_BASE_URL}/Condition"
    params = {"patient": patient_id}
    
    if clinical_status:
        params["clinical-status"] = clinical_status
    
    logger.info(f"Searching Conditions for patient {patient_id}")
    response = _make_request("GET", url, params=params)
    return [entry["resource"] for entry in response.get("entry", [])]


# ==================== MedicationStatement ====================

def search_medications(
    patient_id: str,
    status: Optional[str] = "active"
) -> List[Dict[str, Any]]:
    """
    Search for MedicationStatement resources.
    
    Args:
        patient_id: Patient ID
        status: Filter by status ("active", "completed", "stopped")
        
    Returns:
        List of MedicationStatement resources
    """
    url = f"{FHIR_BASE_URL}/MedicationStatement"
    params = {"patient": patient_id}
    
    if status:
        params["status"] = status
    
    logger.info(f"Searching MedicationStatements for patient {patient_id}")
    response = _make_request("GET", url, params=params)
    return [entry["resource"] for entry in response.get("entry", [])]


# ==================== Procedure ====================

def search_procedures(patient_id: str) -> List[Dict[str, Any]]:
    """
    Search for Procedure resources.
    
    Args:
        patient_id: Patient ID
        
    Returns:
        List of Procedure resources
    """
    url = f"{FHIR_BASE_URL}/Procedure"
    params = {"patient": patient_id, "_sort": "-date"}
    
    logger.info(f"Searching Procedures for patient {patient_id}")
    response = _make_request("GET", url, params=params)
    return [entry["resource"] for entry in response.get("entry", [])]


# ==================== DiagnosticReport ====================

def search_diagnostic_reports(
    patient_id: str,
    category: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search for DiagnosticReport resources.
    
    Args:
        patient_id: Patient ID
        category: Report category (e.g., "LAB", "RAD")
        
    Returns:
        List of DiagnosticReport resources
    """
    url = f"{FHIR_BASE_URL}/DiagnosticReport"
    params = {"patient": patient_id, "_sort": "-date"}
    
    if category:
        params["category"] = category
    
    logger.info(f"Searching DiagnosticReports for patient {patient_id}")
    response = _make_request("GET", url, params=params)
    return [entry["resource"] for entry in response.get("entry", [])]


# ==================== Utility Functions ====================

def extract_patient_name(patient_resource: Dict[str, Any]) -> str:
    """Extract formatted name from Patient resource"""
    names = patient_resource.get("name", [])
    if not names:
        return "Unknown"
    
    name = names[0]
    given = " ".join(name.get("given", []))
    family = name.get("family", "")
    return f"{given} {family}".strip() or "Unknown"


def extract_observation_value(observation: Dict[str, Any]) -> str:
    """Extract value and unit from Observation resource"""
    value_quantity = observation.get("valueQuantity", {})
    if value_quantity:
        value = value_quantity.get("value", "N/A")
        unit = value_quantity.get("unit", "")
        return f"{value} {unit}".strip()
    
    value_string = observation.get("valueString")
    if value_string:
        return value_string
    
    return "N/A"


def extract_code_display(coding_dict: Dict[str, Any]) -> str:
    """Extract human-readable display from a CodeableConcept"""
    if "text" in coding_dict:
        return coding_dict["text"]
    
    codings = coding_dict.get("coding", [])
    if codings:
        return codings[0].get("display", "Unknown")
    
    return "Unknown"


def test_connection() -> bool:
    """
    Test connectivity to the FHIR server.
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        url = f"{FHIR_BASE_URL}/metadata"
        response = _make_request("GET", url)
        logger.info(f"FHIR server connection successful: {FHIR_BASE_URL}")
        return True
    except FHIRClientError as e:
        logger.error(f"FHIR server connection failed: {e}")
        return False

