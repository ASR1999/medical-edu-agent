import pytest
import asyncio
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.services.ehr_mock_provider import MockEHRProvider

# Mock data for testing
MOCK_DATA = {
    "patient_test": {
        "personal_info": {"name": "Test Patient", "age": 30, "gender": "Male"},
        "conditions": [{"name": "Test Condition", "date": "2023-01-01"}],
        "medications": [{"name": "Test Med", "dosage": "10mg", "frequency": "daily"}],
        "recent_labs": [
            {"test_name": "HbA1c", "value": "5.5%", "date": "2023-01-01"},
            {"test_name": "HbA1c", "value": "6.0%", "date": "2023-06-01"}, # Newer
            {"test_name": "Glucose", "value": "100", "date": "invalid-date"}
        ]
    }
}

@pytest.fixture
def mock_provider():
    with patch("app.services.ehr_mock_provider.get_rag_index") as mock_get_rag:
        mock_rag = MagicMock()
        mock_get_rag.return_value = mock_rag
        provider = MockEHRProvider()
        # Inject mock data directly
        provider.db = MOCK_DATA
        return provider

@pytest.mark.asyncio
async def test_get_patient_json(mock_provider):
    data = await mock_provider.get_patient_json("patient_test")
    assert data["personal_info"]["name"] == "Test Patient"

@pytest.mark.asyncio
async def test_patient_exists(mock_provider):
    assert await mock_provider.patient_exists("patient_test") is True
    assert await mock_provider.patient_exists("non_existent") is False

@pytest.mark.asyncio
async def test_get_latest_lab_sorting(mock_provider):
    # Should return the newer HbA1c (2023-06-01)
    result = await mock_provider.get_latest_lab("patient_test", "HbA1c")
    assert result["value"] == "6.0%"
    assert result["date"] == "2023-06-01"

@pytest.mark.asyncio
async def test_get_latest_lab_invalid_date(mock_provider):
    # Should handle invalid date gracefully (return the match found)
    result = await mock_provider.get_latest_lab("patient_test", "Glucose")
    assert result["value"] == "100"

@pytest.mark.asyncio
async def test_get_summary(mock_provider):
    summary = await mock_provider.get_summary("patient_test")
    assert "Test Patient" in summary
    assert "Test Condition" in summary
    assert "Test Med" in summary

@pytest.mark.asyncio
async def test_list_patients(mock_provider):
    patients = await mock_provider.list_patients()
    assert "patient_test" in patients
