from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import os
import uuid
import base64
from langgraph.errors import GraphRecursionError
from typing import Optional, Dict, Any

from app.agents.graph import app_graph, AgentState
from app.services.asr_service import asr_service
from app.services.tts_service import tts_service
from app.services.ehr_provider_factory import get_ehr_provider, get_provider_type
from langchain_core.messages import HumanMessage

from app.config import TEMP_UPLOAD_DIR

router = APIRouter()
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

# Get EHR provider
ehr_provider = get_ehr_provider()

class ChatResponse(BaseModel):
    text_response: str
    audio_response_url: str

@router.post("/chat")
async def chat_endpoint(
    patient_id: str = Form(...),
    text_query: str = Form(None),
    audio_file: UploadFile = File(None),
    image_file: UploadFile = File(None),
    return_json: bool = Form(True)  # New parameter for response format
):
    temp_file_path = None
    temp_audio_path = None
    
    try:
        # --- 1. Handle Input (Text or Audio) ---
        if audio_file:
            # Save temp audio file
            temp_audio_path = os.path.join(TEMP_UPLOAD_DIR, f"{uuid.uuid4()}_{audio_file.filename}")
            with open(temp_audio_path, "wb") as f:
                f.write(await audio_file.read())
            
            # Transcribe
            query = asr_service.transcribe(temp_audio_path)
            
            # Handle transcription errors
            if "Error" in query:
                raise HTTPException(status_code=500, detail=f"ASR Error: {query}")
            
            # Handle empty transcription
            if not query or query.strip() == "":
                raise HTTPException(
                    status_code=400, 
                    detail="Could not transcribe audio. The recording may be empty or unclear. Please try again or use text input."
                )
        elif text_query:
            query = text_query.strip()
            if not query:
                raise HTTPException(status_code=400, detail="Text query cannot be empty.")
        else:
            raise HTTPException(status_code=400, detail="No text query or audio file provided.")
            
        # --- 2. Handle File Upload (Image/PDF) ---
        temp_file_path = None
        if image_file is not None:
            temp_file_path = os.path.join(TEMP_UPLOAD_DIR, f"{uuid.uuid4()}_{image_file.filename}")
            with open(temp_file_path, "wb") as f:
                f.write(await image_file.read())
        
        # --- 3. Run Agent Graph ---
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            patient_id=patient_id,
            file_path=temp_file_path
        )
        
        final_state = await app_graph.ainvoke(initial_state)
        
        # Get the last AI message
        text_response = final_state["messages"][-1].content
        
        # --- 4. Synthesize TTS ---
        audio_output_filename = f"{uuid.uuid4()}_response.wav"
        audio_file_path = tts_service.synthesize(text_response, audio_output_filename)
        
        if "Error" in audio_file_path:
            raise HTTPException(status_code=500, detail=f"TTS Error: {audio_file_path}")

        # --- 5. Return Response (JSON or Audio File) ---
        if return_json:
            # Read audio file and encode as base64 for direct inclusion in response
            audio_base64 = None
            try:
                if os.path.exists(audio_file_path):
                    with open(audio_file_path, "rb") as audio_file:
                        audio_bytes = audio_file.read()
                        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            except Exception as e:
                print(f"Warning: Could not encode audio file: {e}")
                # Continue without base64 audio, frontend can use URL instead
            
            # Return JSON with transcript, audio URL, and base64 audio data
            response_data = {
                "user_query": query,
                "agent_response": text_response,
                "audio_url": f"/api/audio/{audio_output_filename}",
                "audio_path": audio_file_path
            }
            
            # Include base64 audio if available (allows direct playback without separate request)
            if audio_base64:
                response_data["audio_base64"] = audio_base64
                response_data["audio_format"] = "wav"
            
            return JSONResponse(response_data)
        else:
            # Return audio file directly (legacy support)
            return FileResponse(
                path=audio_file_path,
                media_type="audio/wav",
                filename=audio_output_filename
            )

    except GraphRecursionError:
        raise HTTPException(status_code=500, detail="Agent entered an infinite loop.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp files
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        if temp_audio_path and os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


# Serve generated audio files
@router.get("/audio/{filename}")
async def serve_audio(filename: str):
    """Serve generated TTS audio files"""
    audio_path = os.path.join("app/api/generated_audio", filename)
    if not os.path.exists(audio_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=filename
    )

@router.get("/hello")
def hello():
    return {"message": "Hello from Medical Agent API!"}

@router.get("/ehr/{patient_id}")
async def get_ehr(patient_id: str):
    """Verify EHR retrieval: returns both raw JSON and a server-side summary."""
    data = await ehr_provider.get_patient_json(patient_id)
    if not data:
        raise HTTPException(status_code=404, detail="Patient ID not found")
    summary = await ehr_provider.get_summary(patient_id)
    return JSONResponse({"summary": summary, "data": data, "provider": get_provider_type()})


# ==================== RAG & Advanced EHR Endpoints ====================

@router.get("/ehr/{patient_id}/search")
async def ehr_search_endpoint(
    patient_id: str,
    q: str = Query(..., description="Natural language search query"),
    k: int = Query(5, description="Number of results to return"),
    filter_type: Optional[str] = Query(None, description="Filter by data type (condition, medication, lab_result, etc.)")
):
    """
    Perform semantic search over a patient's EHR data using RAG.
    
    This endpoint allows you to verify that RAG is working correctly.
    
    Example: /api/ehr/patient_id_12345/search?q=latest blood sugar&k=3
    """

    if not await ehr_provider.patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient ID not found")
    
    # Index the patient first
    try:
        await ehr_provider.index_patient(patient_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error indexing patient: {str(e)}")
    
    # Perform search
    results = await ehr_provider.rag_search(patient_id, q, k=k, filter_type=filter_type)
    
    return JSONResponse({
        "patient_id": patient_id,
        "query": q,
        "k": k,
        "filter_type": filter_type,
        "results_count": len(results),
        "results": results,
        "provider": get_provider_type()
    })


@router.get("/ehr/{patient_id}/labs")
async def get_patient_labs(patient_id: str, lab_name: Optional[str] = Query(None)):
    """
    Get lab results for a patient.
    
    - Without lab_name: returns all labs
    - With lab_name: returns the latest result for that specific lab
    """
    if not await ehr_provider.patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient ID not found")
    
    if lab_name:
        result = await ehr_provider.get_latest_lab(patient_id, lab_name)
        if not result:
            raise HTTPException(status_code=404, detail=f"Lab '{lab_name}' not found for patient")
        return JSONResponse({"patient_id": patient_id, "lab_name": lab_name, "result": result})
    else:
        labs = await ehr_provider.get_all_labs(patient_id)
        return JSONResponse({"patient_id": patient_id, "labs_count": len(labs), "labs": labs})


@router.get("/ehr/{patient_id}/medications")
async def get_patient_medications(patient_id: str):
    """Get all medications for a patient"""
    if not await ehr_provider.patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient ID not found")
    
    meds = await ehr_provider.get_medications(patient_id)
    return JSONResponse({"patient_id": patient_id, "medications_count": len(meds), "medications": meds})


@router.get("/ehr/{patient_id}/conditions")
async def get_patient_conditions(patient_id: str):
    """Get all conditions for a patient"""
    if not await ehr_provider.patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="Patient ID not found")
    
    conditions = await ehr_provider.get_conditions(patient_id)
    return JSONResponse({"patient_id": patient_id, "conditions_count": len(conditions), "conditions": conditions})


@router.post("/ehr/mock/seed")
async def ehr_mock_seed(payload: Dict[str, Any]):
    """
    Seed the mock EHR database with a new patient (for testing/demo).
    
    Requires:
    - patient_id: string
    - data: complete EHR data dictionary
    
    Note: Only works with Mock provider. Returns error with FHIR provider.
    """
    provider_type = get_provider_type()
    if "Mock" not in provider_type:
        raise HTTPException(
            status_code=400,
            detail=f"Seeding only supported for Mock provider. Current provider: {provider_type}"
        )
    
    if "patient_id" not in payload or "data" not in payload:
        raise HTTPException(status_code=400, detail="Payload must include 'patient_id' and 'data'")
    
    patient_id = payload["patient_id"]
    data = payload["data"]
    
    # Add to provider (in-memory)
    # Note: add_patient is likely synchronous if it's just updating a dict, but if we made everything async...
    # The abstract class doesn't have add_patient, it's specific to Mock. 
    # Let's check if we made it async in MockEHRProvider. 
    # We didn't explicitly change add_patient in the previous step, so it remains sync.
    # However, index_patient IS async now.
    ehr_provider.add_patient(patient_id, data)
    
    # Index for RAG
    await ehr_provider.index_patient(patient_id)
    
    return JSONResponse({
        "status": "success",
        "message": f"Patient {patient_id} added to mock database and indexed",
        "patient_id": patient_id
    })


@router.get("/ehr/patients")
async def list_patients():
    """List all available patient IDs"""
    patients = await ehr_provider.list_patients()
    return JSONResponse({
        "provider": get_provider_type(),
        "patients_count": len(patients),
        "patients": patients
    })


@router.get("/system/provider")
async def get_system_provider():
    """Get information about the active EHR provider"""
    patients = await ehr_provider.list_patients()
    return JSONResponse({
        "provider_type": get_provider_type(),
        "patients_available": len(patients)
    })


# ==================== Testing Endpoints ====================

@router.post("/test/transcribe")
async def test_transcribe(audio_file: UploadFile = File(...)):
    """Test ASR service directly"""
    temp_path = os.path.join(TEMP_UPLOAD_DIR, f"test_{uuid.uuid4()}_{audio_file.filename}")
    try:
        with open(temp_path, "wb") as f:
            f.write(await audio_file.read())
        
        transcription = asr_service.transcribe(temp_path)
        return JSONResponse({
            "transcription": transcription,
            "model": "medasr-v2-ct2",
            "status": "success" if "Error" not in transcription else "error"
        })
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/test/synthesize")
async def test_synthesize(text: str = Form(...)):
    """Test TTS service directly"""
    output_filename = f"test_{uuid.uuid4()}_tts.wav"
    audio_path = tts_service.synthesize(text, output_filename)
    
    if "Error" in audio_path:
        raise HTTPException(status_code=500, detail=audio_path)
    
    return FileResponse(
        path=audio_path,
        media_type="audio/wav",
        filename=output_filename
    )