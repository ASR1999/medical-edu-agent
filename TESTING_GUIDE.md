# 🧪 Complete Testing Guide - Medical AI Agent

## 📋 Table of Contents

1. [Prerequisites & Environment Setup](#prerequisites--environment-setup)
2. [Starting All Services](#starting-all-services)
3. [Service-by-Service Testing](#service-by-service-testing)
4. [Integration Testing](#integration-testing)
5. [EHR System Testing](#ehr-system-testing)
6. [Frontend Testing](#frontend-testing)
7. [Performance Testing](#performance-testing)
8. [Debugging & Troubleshooting](#debugging--troubleshooting)

---

## Prerequisites & Environment Setup

### 1. Verify Installation

```bash
# Check Python
python3 --version  # Should be 3.10+

# Check Node.js
node --version  # Should be 18+

# Check Docker (optional)
docker --version
docker-compose --version

# Check pip packages
pip list | grep -E "fastapi|langchain|faster-whisper|chromadb"
```

### 2. Configure Environment Files

```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent

# Backend configuration
cp backend/ENV_EXAMPLE backend/.env
nano backend/.env  # Add your API keys:
# GROQ_API_KEY=your_key_here
# SERPER_API_KEY=your_key_here

# Frontend configuration
cp frontend/ENV_EXAMPLE frontend/.env
echo "VITE_API_URL=http://localhost:8000/api" > frontend/.env
```

### 3. Convert ASR Model (If Not Done)

```bash
cd ml-training

# Install conversion dependencies
pip install ctranslate2>=3.20.0 transformers>=4.35.0 torch

# Run conversion
./convert_to_ct2.sh

# Verify
ls -la ../backend/ct2_models/medasr-v2-ct2/
# Should see: model.bin, config.json, vocabulary.json

cd ..
```

---

## Starting All Services

### Option A: Docker Compose (Recommended)

```bash
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f hapi-fhir
```

**Services will be available at:**
- ✅ Backend: http://localhost:8000
- ✅ Frontend: http://localhost:5173
- ✅ API Docs: http://localhost:8000/docs
- ✅ FHIR Server: http://localhost:8080/fhir

### Option B: Local Development (Manual)

#### Terminal 1: Backend

```bash
cd backend

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
✅ ASR Service: Loaded model from ct2_models/medasr-v2-ct2 on cuda (float16)
✅ TTS Service initialized
✅ EHR Provider: MockEHRProvider loaded with 5 patients
```

#### Terminal 2: Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
  VITE v4.4.5  ready in 823 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h to show help
```

#### Terminal 3: FHIR Server (Optional)

```bash
docker run -p 8080:8080 \
  -e HAPI_FHIR_ALLOW_EXTERNAL_REFERENCES=true \
  -e HAPI_FHIR_ALLOW_MULTIPLE_DELETE=true \
  --name hapi-fhir \
  hapiproject/hapi:latest
```

**Expected Output:**
```
Server started successfully on port 8080
FHIR endpoint available at: /fhir
```

---

## Service-by-Service Testing

### 1. Backend API Testing

#### Test 1.1: Basic Connectivity

```bash
curl http://localhost:8000/api/hello
```

**Expected:**
```json
{"message": "Hello from Medical Agent API!"}
```

#### Test 1.2: API Documentation

Open in browser: http://localhost:8000/docs

**Expected:** Interactive Swagger UI with all endpoints listed

#### Test 1.3: System Provider Info

```bash
curl http://localhost:8000/api/system/provider | jq
```

**Expected:**
```json
{
  "provider_type": "mock",
  "patients_available": 5
}
```

---

### 2. ASR Service Testing

#### Test 2.1: Check ASR Status

Look for this line in backend startup logs:
```
✅ ASR Service: Loaded model from ct2_models/medasr-v2-ct2 on cuda (float16)
```

#### Test 2.2: Test ASR with Audio File

```bash
# Create a test audio file or use existing one
curl -X POST http://localhost:8000/api/test/transcribe \
  -F "audio_file=@path/to/test_audio.wav" | jq
```

**Expected:**
```json
{
  "transcription": "What medications am I taking?",
  "model": "medasr-v2-ct2",
  "status": "success"
}
```

#### Test 2.3: Record Audio from Browser

1. Open: http://localhost:5173
2. Click microphone button (should turn red)
3. Say: "What are my conditions?"
4. Click stop button
5. Check backend logs for transcription output

**Expected in logs:**
```
📝 ASR Transcription: What are my conditions?
```

---

### 3. TTS Service Testing

#### Test 3.1: Synthesize Speech

```bash
curl -X POST http://localhost:8000/api/test/synthesize \
  -F "text=Hello, this is a test of the text to speech system" \
  --output test_tts.wav
```

**Expected:**
- File `test_tts.wav` created
- File size ~200-500 KB

#### Test 3.2: Play Audio

```bash
# Linux
play test_tts.wav
# or
aplay test_tts.wav

# macOS
afplay test_tts.wav

# Windows
start test_tts.wav
```

**Expected:** Clear voice reading the text

---

### 4. EHR System Testing

#### Test 4.1: List All Patients

```bash
curl http://localhost:8000/api/ehr/patients | jq
```

**Expected:**
```json
{
  "patients_count": 5,
  "patients": [
    "patient_id_12345",
    "patient_id_67890",
    "patient_id_24680",
    "patient_id_13579",
    "patient_id_98765"
  ]
}
```

#### Test 4.2: Get Patient Data

```bash
curl http://localhost:8000/api/ehr/patient_id_12345 | jq
```

**Expected:**
```json
{
  "summary": "=== EHR Summary for Jane Doe ===\nDemographics: 42 years old, Female...",
  "data": {
    "personal_info": {
      "name": "Jane Doe",
      "age": 42,
      "gender": "Female"
    },
    "conditions": [...],
    "medications": [...],
    "recent_labs": [...]
  },
  "provider": "mock"
}
```

#### Test 4.3: Get Specific Lab Results

```bash
# Get all labs
curl http://localhost:8000/api/ehr/patient_id_12345/labs | jq

# Get specific lab
curl "http://localhost:8000/api/ehr/patient_id_12345/labs?lab_name=HbA1c" | jq
```

**Expected:**
```json
{
  "patient_id": "patient_id_12345",
  "lab_name": "HbA1c",
  "result": {
    "test_name": "HbA1c",
    "value": "7.2%",
    "date": "2025-10-20",
    "notes": "Slightly elevated..."
  }
}
```

#### Test 4.4: Get Medications

```bash
curl http://localhost:8000/api/ehr/patient_id_12345/medications | jq
```

**Expected:**
```json
{
  "patient_id": "patient_id_12345",
  "medications_count": 2,
  "medications": [
    {
      "name": "Metformin",
      "dosage": "500mg",
      "frequency": "Twice daily"
    },
    {
      "name": "Lisinopril",
      "dosage": "10mg",
      "frequency": "Once daily"
    }
  ]
}
```

#### Test 4.5: Get Conditions

```bash
curl http://localhost:8000/api/ehr/patient_id_12345/conditions | jq
```

**Expected:**
```json
{
  "patient_id": "patient_id_12345",
  "conditions_count": 2,
  "conditions": [
    {
      "name": "Type 2 Diabetes",
      "diagnosed_on": "2020-03-15"
    },
    {
      "name": "Hypertension",
      "diagnosed_on": "2019-08-22"
    }
  ]
}
```

---

### 5. RAG (Semantic Search) Testing

#### Test 5.1: Basic RAG Search

```bash
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=5" | jq
```

**Expected:**
```json
{
  "patient_id": "patient_id_12345",
  "query": "diabetes",
  "k": 5,
  "filter_type": null,
  "results_count": 5,
  "results": [
    {
      "text": "conditions[0].name: Type 2 Diabetes",
      "metadata": {
        "patient_id": "patient_id_12345",
        "path": "conditions[0].name",
        "type": "condition"
      },
      "score": 0.85
    },
    ...
  ]
}
```

**Quality Check:**
- `results_count` should be > 0
- Top result `score` should be > 0.5 (higher = more relevant)
- Results should mention diabetes-related data

#### Test 5.2: Medical Term Search

```bash
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=hypertension+blood+pressure&k=3" | jq
```

**Expected:** Results about blood pressure, hypertension, Lisinopril

#### Test 5.3: Layman Term Search

```bash
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=high+blood+pressure&k=3" | jq
```

**Expected:** Similar results to Test 5.2 (RAG understands synonyms)

#### Test 5.4: Filtered Search

```bash
# Only lab results
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=blood+test&k=5&filter_type=lab_result" | jq

# Only medications
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes+medicine&k=5&filter_type=medication" | jq
```

---

### 6. AI Agent Testing

#### Test 6.1: Simple Text Chat

```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What medications am I taking?" \
  -F "return_json=true" | jq
```

**Expected:**
```json
{
  "user_query": "What medications am I taking?",
  "agent_response": "Based on your medical records, you are currently taking:\n\n1. Metformin 500mg - Twice daily...\n\n📊 Data sources used: EHR-Medications\n⚠️ This is educational information...",
  "audio_url": "/api/audio/abc123_response.wav"
}
```

**Check backend logs for:**
```
Node: sos_check
Node: call_model
Node: call_tools
[TOOL] ehr_get_medications: Fetching medications for patient patient_id_12345
Node: call_model
```

#### Test 6.2: Complex Query (Multiple Tools)

```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=Given my diabetes, what do my recent lab results mean?" \
  -F "return_json=true" | jq
```

**Expected backend logs:**
```
[TOOL] ehr_get_conditions: Fetching conditions for patient patient_id_12345
[TOOL] ehr_rag_search: Searching EHR for patient patient_id_12345
[TOOL] ehr_get_all_labs: Fetching all labs for patient patient_id_12345
```

**Response should:**
- Mention "Type 2 Diabetes"
- Discuss HbA1c 7.2%
- Explain significance
- Cite multiple sources

#### Test 6.3: General Question (No EHR)

```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What is diabetes?" \
  -F "return_json=true" | jq
```

**Expected backend logs:**
```
[TOOL] web_search: Searching for: what is diabetes
```

**Should NOT see EHR tool calls unless agent personalizes the answer.**

#### Test 6.4: Audio Input Chat

```bash
# With audio file
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "audio_file=@test_audio.wav" \
  -F "return_json=true" | jq
```

**Backend logs should show:**
```
📝 ASR Transcription: [your spoken question]
[TOOL] [appropriate tool calls]
```

#### Test 6.5: Image Upload (Vision)

```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=Analyze this medical image" \
  -F "image_file=@path/to/xray.jpg" \
  -F "return_json=true" | jq
```

**Expected backend logs:**
```
[VISION] Processing file: xray.jpg
[TOOL] analyze_medical_image: Analyzing image for patient patient_id_12345
```

---

### 7. Frontend Application Testing

#### Test 7.1: Load Frontend

1. Open: http://localhost:5173
2. **Expected:** Modern UI with gradient header, chat area, patient selector

#### Test 7.2: Patient Selector

1. Click patient dropdown in header
2. **Expected:** See 5 patients:
   - Jane Doe (42F) - Type 2 Diabetes, Hypertension
   - John Smith (58M) - Coronary Artery Disease
   - Maria Garcia (35F) - Asthma
   - Robert Johnson (67M) - Osteoarthritis
   - Sarah Chen (29F) - PCOS, Hypothyroidism

3. Select different patient
4. **Expected:** EHR sidebar updates (if open), chat history clears

#### Test 7.3: Text Chat

1. Type in input: "What medications am I taking?"
2. Click send button (paper plane icon)
3. **Expected:**
   - User message appears with text
   - Loading indicator shows
   - AI response appears with:
     - Text transcript
     - Audio player
     - Source citations ("📊 Sources: ...")
   - Audio auto-plays

#### Test 7.4: Voice Input

1. Click microphone button (turns red/pulsing)
2. Speak: "What are my conditions?"
3. Click stop button
4. **Expected:**
   - Recording stops
   - User message shows with audio player
   - Backend transcribes
   - AI responds with text + audio

#### Test 7.5: File Upload

1. Locate file upload area (above input box)
2. Drag & drop an image (PNG/JPG) or PDF
3. **Expected:**
   - File preview appears with filename and size
   - X button to remove file

4. Type: "Analyze this image"
5. Click send
6. **Expected:**
   - File uploads with query
   - Vision agent processes
   - Response includes image analysis

#### Test 7.6: EHR Sidebar

1. Click hamburger menu (☰) in top-right
2. **Expected:** Sidebar slides in from right showing:
   - Patient demographics
   - Conditions (red section)
   - Medications (green section)
   - Recent labs (purple section)
   - Doctor's notes (yellow section)

3. Click X to close
4. **Expected:** Sidebar slides out

#### Test 7.7: Responsive Design

1. Resize browser window to mobile size
2. **Expected:**
   - Patient selector moves below header
   - Chat area adjusts
   - Sidebar becomes full overlay

#### Test 7.8: Error Handling

1. Stop backend (Ctrl+C)
2. Try sending a message
3. **Expected:**
   - Error message displays in chat
   - User can retry when backend restarts

---

### 8. FHIR Server Testing (Optional)

#### Test 8.1: FHIR Server Health

```bash
curl http://localhost:8080/fhir/metadata | jq '.fhirVersion'
```

**Expected:** FHIR version (e.g., "4.0.1")

#### Test 8.2: Switch to FHIR Provider

```bash
# Edit backend/.env
echo "EHR_PROVIDER=fhir" >> backend/.env

# Restart backend
# In docker: docker-compose restart backend
# In local: Ctrl+C and restart uvicorn
```

#### Test 8.3: Create FHIR Patient

```bash
curl -X POST http://localhost:8080/fhir/Patient \
  -H "Content-Type: application/fhir+json" \
  -d '{
    "resourceType": "Patient",
    "id": "test-patient-001",
    "name": [{"given": ["Test"], "family": "Patient"}],
    "gender": "male",
    "birthDate": "1980-01-01"
  }'
```

#### Test 8.4: Query FHIR Patient via Backend

```bash
curl http://localhost:8000/api/ehr/test-patient-001 | jq
```

**Expected:** Patient data from FHIR server

---

## Integration Testing

### Automated Integration Tests

```bash
cd scripts
python test_integration.py
```

**Expected Output:**
```
🧪 MEDICAL AI AGENT - INTEGRATION TESTS
=========================================
API Base URL: http://localhost:8000/api

Running: Basic API...
✅ API Connectivity: PASS
   Hello from Medical Agent API!

Running: EHR Provider...
✅ EHR Provider: PASS
   Type: mock, Patients: 5

Running: Patient List...
✅ List Patients: PASS
   5 patients available

Running: EHR Retrieval...
✅ EHR Retrieval: PASS
   Retrieved data for Jane Doe

Running: RAG Search...
✅ RAG Search: PASS
   Found 5 results for 'diabetes medications'

Running: TTS Synthesis...
✅ TTS Synthesis: PASS
   Generated 245.3 KB audio

Running: Full Chat Pipeline...
   Sending query: 'What medications am I taking?'
✅ Chat Pipeline (Text): PASS
   Response length: 487 chars
   Preview: Based on your medical records...
   Audio: /api/audio/abc123_response.wav

📊 TEST SUMMARY
=========================================
✅ PASS - Basic API
✅ PASS - EHR Provider
✅ PASS - Patient List
✅ PASS - EHR Retrieval
✅ PASS - RAG Search
✅ PASS - TTS Synthesis
✅ PASS - Full Chat Pipeline

7/7 tests passed (100%)
Total time: 45.23s

🎉 All tests passed! System is ready.
```

### Manual End-to-End Test

**Scenario:** Patient asks about lab results

1. **Start:** Open http://localhost:5173
2. **Select Patient:** Choose "Jane Doe"
3. **Ask Question:** Type: "What was my latest HbA1c?"
4. **Verify Response:**
   - Shows loading indicator
   - AI responds with: "Your latest HbA1c test on October 20, 2025 was 7.2%..."
   - Audio plays automatically
   - Sources cited: "📊 Data sources used: EHR-RAG, Patient Labs"
   - Medical disclaimer present
5. **Check Backend Logs:**
   ```
   📝 ASR Transcription: What was my latest HbA1c?
   Node: sos_check
   Node: call_model
   Node: call_tools
   [TOOL] ehr_rag_search: Searching EHR for patient patient_id_12345
   [TOOL] ehr_get_latest_lab: Fetching 'HbA1c' for patient patient_id_12345
   Node: call_model
   ```
6. **Check EHR Sidebar:**
   - Click ☰ menu
   - Verify shows HbA1c: 7.2% in Recent Labs section

**Pass Criteria:**
- ✅ Specific value (7.2%) mentioned
- ✅ Correct date (October 20, 2025)
- ✅ Tool calls logged
- ✅ Sources cited
- ✅ Audio plays

---

## Performance Testing

### Response Time Benchmarks

```bash
# Test EHR retrieval speed
time curl http://localhost:8000/api/ehr/patient_id_12345 > /dev/null

# Test RAG search speed
time curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=5" > /dev/null

# Test full chat pipeline
time curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What are my conditions?" \
  -F "return_json=true" > /dev/null
```

**Expected Times (with GPU):**
- EHR Retrieval: < 0.2s
- RAG Search: < 1s
- Full Chat: < 8s

### Load Testing

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test EHR endpoint
ab -n 100 -c 10 http://localhost:8000/api/ehr/patient_id_12345

# Test RAG
ab -n 50 -c 5 "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=3"
```

**Expected:**
- Requests/sec: > 50 for EHR
- Mean response: < 200ms

---

## Debugging & Troubleshooting

### Common Issues

#### 1. "Connection refused" on http://localhost:8000

**Diagnosis:**
```bash
# Check if backend is running
curl http://localhost:8000/api/hello

# Check port usage
lsof -i :8000
```

**Fix:**
```bash
# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. "ASR model not loaded"

**Diagnosis:**
```bash
ls backend/ct2_models/medasr-v2-ct2/
# Should see: model.bin, config.json, etc.
```

**Fix:**
```bash
cd ml-training
./convert_to_ct2.sh
```

#### 3. RAG returns no results

**Diagnosis:**
```bash
# Check if patient is indexed
curl http://localhost:8000/api/ehr/patients
```

**Fix:**
```bash
# Force reindex by searching
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=test&k=1"
```

#### 4. Frontend can't connect to backend

**Diagnosis:**
```bash
# Check frontend .env
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000/api
```

**Fix:**
```bash
echo "VITE_API_URL=http://localhost:8000/api" > frontend/.env
# Restart frontend: npm run dev
```

#### 5. Docker containers won't start

**Diagnosis:**
```bash
docker-compose ps
docker-compose logs
```

**Fix:**
```bash
# Clean restart
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Verbose Logging

```bash
# Enable verbose backend logs
export LANGCHAIN_VERBOSE=true
export LANGCHAIN_TRACING_V2=false

# Start backend with debug
uvicorn app.main:app --reload --log-level debug

# Or in docker-compose.yml, add:
# environment:
#   - LANGCHAIN_VERBOSE=true
```

---

## Test Checklist

Use this checklist to verify complete system functionality:

### Backend Services
- [ ] API responds at /api/hello
- [ ] ASR model loads successfully
- [ ] TTS synthesizes audio
- [ ] EHR provider loads 5 patients
- [ ] RAG index is accessible
- [ ] All EHR endpoints work

### AI Agent
- [ ] Agent invokes tools for patient queries
- [ ] RAG search returns relevant results
- [ ] Agent cites data sources
- [ ] Medical disclaimer included
- [ ] Handles missing data gracefully

### Frontend
- [ ] Application loads at :5173
- [ ] Patient selector works
- [ ] Text input sends messages
- [ ] Voice recording works
- [ ] File upload works
- [ ] Audio playback works
- [ ] EHR sidebar displays
- [ ] Responsive on mobile

### Integration
- [ ] End-to-end chat cycle completes
- [ ] Specific EHR data appears in responses
- [ ] Source citations visible
- [ ] All 7 integration tests pass

---

## 🎉 Success Criteria

Your system is fully functional if:

✅ All automated tests pass (7/7)  
✅ Backend logs show tool invocations  
✅ Agent responses include specific EHR values  
✅ Sources are cited in every response  
✅ RAG search returns relevant results (score > 0.5)  
✅ Frontend displays complete UI with all features  
✅ End-to-end: Voice → ASR → Agent → TTS works  

**If all criteria met: System is production-ready! 🚀**

---

*Last Updated: October 27, 2025*
