import sys
from unittest.mock import MagicMock

# Mock services before importing app
mock_tts = MagicMock()
mock_asr = MagicMock()
sys.modules["app.services.tts_service"] = MagicMock(tts_service=mock_tts)
sys.modules["app.services.asr_service"] = MagicMock(asr_service=mock_asr)
sys.modules["MeloTTS"] = MagicMock() # Mock MeloTTS package

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/api/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello from Medical Agent API!"}

def test_get_system_provider():
    response = client.get("/api/system/provider")
    assert response.status_code == 200
    data = response.json()
    assert "provider_type" in data
    assert "patients_available" in data
