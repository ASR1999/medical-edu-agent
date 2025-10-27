# 🚀 Complete Setup & Run Guide

## Overview
This guide provides all commands and steps to set up, convert models, and run the complete medical AI application.

---

## 📋 Prerequisites

```bash
# System requirements
- Python 3.11+
- Node.js 20+
- 8GB RAM minimum (16GB recommended)
- GPU optional (faster inference)

# API Keys needed
- GROQ_API_KEY (for LLM)
- OPENAI_API_KEY (for vision analysis)
- SERPER_API_KEY (for web search)
```

---

## 🔄 STEP 1: Convert medasr-v2 Model to CTranslate2

Your medical-grade Whisper model needs to be converted for faster inference.

### Commands:

```bash
# Navigate to ml-training directory
cd /home/uwcuser/nltk_data/mtech-medical-agent/ml-training

# Make script executable
chmod +x convert_to_ct2.sh

# Install conversion dependencies
pip install ctranslate2>=3.20.0 transformers>=4.35.0

# Run conversion (takes 2-5 minutes)
./convert_to_ct2.sh

# Or run Python script directly:
python convert_to_ct2.py
```

### What This Does:
- Reads HuggingFace model from `ml-training/medasr-v2/`
- Converts to CTranslate2 format (faster, optimized)
- Saves to `backend/ct2_models/medasr-v2-ct2/`
- Applies float16 quantization (2x smaller, minimal quality loss)

### Verify Conversion:
```bash
ls -lh ../backend/ct2_models/medasr-v2-ct2/
# Should see: model.bin (large file), config.json, vocab files
```

---

## ⚙️ STEP 2: Configure Backend

### Setup Environment Variables:

```bash
cd ../backend
cp ENV_EXAMPLE .env
nano .env  # or use your favorite editor
```

### Minimal .env Configuration:

```env
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
SERPER_API_KEY=your_serpapi_key_here

# ASR Model Path (auto-configured after conversion)
ASR_MODEL_PATH=app/../ct2_models/medasr-v2-ct2
ASR_DEVICE=cuda  # or "cpu"
ASR_COMPUTE_TYPE=float16  # or "int8" for CPU

# EHR Provider
EHR_PROVIDER=mock  # Start with mock, switch to "fhir" later

# Optional: AWS for vision uploads (can skip initially)
# AWS_ACCESS_KEY=
# AWS_SECRET_KEY=
# S3_BUCKET_NAME=
```

---

## 📦 STEP 3: Install Dependencies

### Backend:

```bash
cd backend
pip install -r requirements.txt

# If you get errors, install these individually:
pip install fastapi uvicorn[standard]
pip install langgraph langchain langchain_groq langchain-openai langchain-community
pip install faster-whisper chromadb sentence-transformers
pip install MeloTTS soundfile
```

### Frontend:

```bash
cd ../frontend
npm install

# If errors, try:
npm install --legacy-peer-deps
```

---

## 🚀 STEP 4: Run the Application

### Option A: Run Locally (Development)

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

**Access:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### Option B: Run with Docker

```bash
# From project root
docker compose up --build

# Or run in background:
docker compose up -d
```

**Access:**
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- HAPI FHIR: http://localhost:8080

---

## 🧪 STEP 5: Test the System

### Test 1: Check ASR Model Loaded

```bash
curl http://localhost:8000/api/hello
# Should return: {"message": "Hello from Medical Agent API!"}

# Check backend console for:
# ✅ ASR Service: Loaded model from .../medasr-v2-ct2 on cuda (float16)
```

### Test 2: Test EHR System

```bash
# Get patient data
curl http://localhost:8000/api/ehr/patient_id_12345 | jq

# Test RAG search
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=3" | jq
```

### Test 3: Test Chat (Text)

```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What is my latest HbA1c?" \
  --output response.wav

# Play audio
play response.wav  # Linux/Mac
# or open response.wav in media player
```

### Test 4: Frontend Chat

1. Open http://localhost:5173
2. Type: "What medications am I taking?"
3. Verify:
   - ASR transcription (if using audio)
   - Agent uses EHR tools (check backend logs)
   - Response includes patient-specific data
   - Source citations shown

---

## 📊 Monitoring

### Backend Logs:
Watch for these indicators of correct operation:

```
✅ ASR Service: Loaded model from ...
✅ EHR Service: Mock database loaded
[TOOL] ehr_rag_search: Searching EHR for patient patient_id_12345
[TOOL] ehr_get_medications: Fetching medications for patient patient_id_12345
📝 ASR Transcription: What is my latest HbA1c
```

### Performance Benchmarks:
- ASR (10s audio): <2s
- RAG search: <500ms
- Full chat cycle: <8s

---

## 🐛 Troubleshooting

### Issue: "ASR model not loaded"
**Solution:**
```bash
# 1. Verify model was converted
ls backend/ct2_models/medasr-v2-ct2/model.bin

# 2. Check path in backend/.env
grep ASR_MODEL_PATH backend/.env

# 3. Re-run conversion if needed
cd ml-training && ./convert_to_ct2.sh
```

### Issue: "Patient ID not found"
**Solution:** Use one of the 5 mock patient IDs:
- `patient_id_12345` (Jane Doe - Diabetes)
- `patient_id_67890` (John Smith - CAD)
- `patient_id_24680` (Maria Garcia - Asthma)
- `patient_id_13579` (Robert Johnson - Arthritis)
- `patient_id_98765` (Sarah Chen - PCOS)

### Issue: Frontend can't connect to backend
**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/api/hello

# Check frontend .env
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000/api
```

### Issue: Agent doesn't use EHR tools
**Check:**
1. Backend logs show `[TOOL]` messages
2. System prompt includes tool instructions
3. LLM is `llama3-70b-8192` (not smaller model)

---

## 📈 Frontend Improvements (Planned)

The current frontend is functional but basic. Planned enhancements:

1. **Patient Selector** - Dropdown to switch between patients
2. **Transcript Display** - Show text alongside audio
3. **File Upload UI** - Drag-drop for medical images
4. **EHR Sidebar** - Show patient summary
5. **Source Citations** - Display "Data sources used"
6. **Better Loading States** - Progress indicators
7. **Error Handling** - User-friendly error messages

These are in `IMPLEMENTATION_PLAN.md` and ready to be implemented.

---

## 🎯 Quick Start Checklist

- [ ] Convert medasr-v2 to CT2 format (`./convert_to_ct2.sh`)
- [ ] Configure backend/.env with API keys
- [ ] Install backend dependencies (`pip install -r requirements.txt`)
- [ ] Install frontend dependencies (`npm install`)
- [ ] Start backend (`uvicorn app.main:app --reload`)
- [ ] Start frontend (`npm run dev`)
- [ ] Test with: "What is my latest HbA1c?"
- [ ] Verify backend logs show tool usage
- [ ] Check response cites EHR data

---

## 📚 Additional Resources

- **README.md** - Full project documentation
- **TESTING_GUIDE.md** - Comprehensive testing procedures
- **IMPLEMENTATION_PLAN.md** - Detailed improvement plan
- **API Docs** - http://localhost:8000/docs (when running)

---

## 🆘 Getting Help

If you encounter issues:

1. Check backend console for error messages
2. Verify all dependencies installed
3. Ensure API keys are valid
4. Check model files exist
5. Review logs for `[TOOL]` invocations
6. Test individual components (ASR, EHR, RAG)

---

## ✅ Success Indicators

Your system is working correctly when you see:

1. **Backend startup:**
   ```
   ✅ ASR Service: Loaded model from ...
   ✅ EHR Service: Mock database loaded
   LangGraph compiled. 🚀
   ```

2. **Chat query:**
   ```
   🎤 ASR Service: Transcribing...
   [TOOL] ehr_rag_search: Searching EHR...
   [TOOL] ehr_get_latest_lab: Fetching 'HbA1c'...
   ```

3. **Agent response** includes:
   - Specific values from patient EHR
   - "📊 Data sources used: EHR-RAG, Patient Labs"
   - Clear, jargon-free explanation

---

## 🎉 You're Ready!

Follow the steps above and your medical AI assistant will be fully operational with:
- ✅ Medical-grade ASR (medasr-v2)
- ✅ EHR integration with RAG search
- ✅ Intelligent agent with tool use
- ✅ Voice input and output
- ✅ Medical image analysis
- ✅ Source attribution

Enjoy building! 🩺🤖

