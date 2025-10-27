# 🚀 Quick Start Guide - Medical AI Agent

## ✅ Prerequisites Checklist

Before starting, ensure you have:

- [ ] Python 3.10+ installed
- [ ] Node.js 18+ and npm installed
- [ ] Docker and Docker Compose installed (for containerized setup)
- [ ] API Keys ready:
  - Groq API Key (for LLM)
  - SerperAPI Key (for web search)
  - AWS credentials (optional, for vision agent)

---

## 📁 Project Structure

```
mtech-medical-agent/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── agents/            # LangGraph agent & tools
│   │   ├── api/               # API endpoints
│   │   ├── services/          # ASR, TTS, EHR, RAG services
│   │   └── data/              # Mock EHR data & RAG index
│   ├── ct2_models/            # CTranslate2 models for ASR
│   └── requirements.txt
├── frontend/                  # React + Vite frontend
│   ├── src/
│   │   ├── components/        # UI components
│   │   └── hooks/             # React hooks
│   └── package.json
├── ml-training/               # Model training & conversion
│   ├── medasr-v2/            # Fine-tuned Whisper model (HF format)
│   ├── convert_to_ct2.py     # CT2 conversion script
│   └── convert_to_ct2.sh
├── scripts/                   # Testing scripts
└── docker-compose.yml
```

---

## 🔧 Setup Instructions

### Option 1: Docker Setup (Recommended)

**Step 1: Clone and Configure**
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent

# Backend environment
cp backend/ENV_EXAMPLE backend/.env
# Edit backend/.env with your API keys
nano backend/.env

# Frontend environment
cp frontend/ENV_EXAMPLE frontend/.env
nano frontend/.env
```

**Step 2: Convert ASR Model to CT2**
```bash
cd ml-training
./convert_to_ct2.sh
cd ..
```

**Step 3: Build and Run**
```bash
docker-compose up --build
```

**Access the Application:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api
- FHIR Server: http://localhost:8080/fhir
- API Docs: http://localhost:8000/docs

---

### Option 2: Local Development Setup

**Step 1: Backend Setup**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp ENV_EXAMPLE .env
nano .env  # Add your API keys

# Convert ASR model
cd ../ml-training
./convert_to_ct2.sh
cd ../backend

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Step 2: Frontend Setup** (in a new terminal)
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp ENV_EXAMPLE .env
echo "VITE_API_URL=http://localhost:8000/api" > .env

# Run frontend
npm run dev
```

**Step 3: HAPI FHIR Server** (optional, in a new terminal)
```bash
docker run -p 8080:8080 \
  -e HAPI_FHIR_ALLOW_EXTERNAL_REFERENCES=true \
  hapiproject/hapi:latest
```

---

## 🔑 Environment Configuration

### Backend `.env` (Essential Variables)

```bash
# === LLM Configuration ===
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.1-70b-versatile

# === Search API ===
SERPER_API_KEY=your_serper_api_key_here

# === EHR Provider ===
EHR_PROVIDER=mock  # Options: mock, fhir, hybrid
FHIR_BASE_URL=http://localhost:8080/fhir

# === ASR Configuration ===
ASR_MODEL_PATH=ct2_models/medasr-v2-ct2
ASR_DEVICE=cuda  # or cpu
ASR_COMPUTE_TYPE=float16  # or int8 for CPU
```

### Frontend `.env`

```bash
VITE_API_URL=http://localhost:8000/api
```

---

## 🧪 Testing the System

### 1. Run Integration Tests
```bash
cd scripts
python test_integration.py
```

### 2. Manual Testing via API

**Test ASR:**
```bash
curl -X POST http://localhost:8000/api/test/transcribe \
  -F "audio_file=@test_audio.wav"
```

**Test TTS:**
```bash
curl -X POST http://localhost:8000/api/test/synthesize \
  -F "text=Hello, this is a test" \
  --output test_output.wav
```

**Test EHR Retrieval:**
```bash
curl http://localhost:8000/api/ehr/patient_id_12345 | jq
```

**Test RAG Search:**
```bash
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=5" | jq
```

**Test Full Chat:**
```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What medications am I taking?" \
  -F "return_json=true" | jq
```

---

## 🎯 Using the Application

### Frontend Features

1. **Patient Selector** - Switch between 5 demo patients
2. **Text Input** - Type questions about health
3. **Voice Input** - Click microphone to record voice questions
4. **File Upload** - Drag & drop medical images/PDFs
5. **EHR Sidebar** - View patient medical history
6. **Transcript Display** - See both text and audio responses
7. **Source Citations** - See which EHR tools were used

### Sample Questions to Try

- "What was my latest HbA1c result?"
- "What medications am I currently taking?"
- "Tell me about my diabetes diagnosis"
- "What do my recent lab results show?"
- "Can you explain my blood pressure medication?"

---

## 🐛 Troubleshooting

### ASR Model Not Found
```bash
# Convert the model
cd ml-training
./convert_to_ct2.sh

# Verify it exists
ls -la ../backend/ct2_models/medasr-v2-ct2/
```

### CUDA Out of Memory
```bash
# In backend/.env, switch to CPU:
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

### Frontend Can't Connect to Backend
```bash
# Check backend is running
curl http://localhost:8000/api/hello

# Check frontend .env has correct URL
cat frontend/.env
# Should show: VITE_API_URL=http://localhost:8000/api
```

### RAG Index Not Working
```bash
# Re-index a patient
curl -X POST "http://localhost:8000/api/ehr/patient_id_12345/search?q=test&k=1"

# This will auto-index if not already indexed
```

### Docker Build Fails
```bash
# Clean and rebuild
docker-compose down
docker system prune -a
docker-compose up --build
```

---

## 📊 System Architecture

```
┌─────────────┐
│  Frontend   │  React + Vite
│  (Port 5173)│  - Patient selector
└──────┬──────┘  - Chat interface
       │         - File upload
       │         - EHR sidebar
       ▼
┌─────────────┐
│   Backend   │  FastAPI
│  (Port 8000)│  - /api/chat (main endpoint)
└──────┬──────┘  - /api/ehr/* (EHR endpoints)
       │         - /api/test/* (testing)
       │
   ┌───┴────┬──────────┬──────────┐
   ▼        ▼          ▼          ▼
┌──────┐ ┌──────┐ ┌─────────┐ ┌─────┐
│ ASR  │ │ LLM  │ │   EHR   │ │ TTS │
│Whisper│ │ Groq │ │Mock/FHIR│ │Melo │
└──────┘ └──┬───┘ └────┬────┘ └─────┘
           │          │
      ┌────┴──────────┴────┐
      │   LangGraph Agent   │
      │   - EHR tools       │
      │   - RAG search      │
      │   - Web search      │
      │   - Vision analysis │
      └─────────────────────┘
```

---

## 🔄 Workflow

1. **User Input** → Text or Voice (via frontend)
2. **ASR** → Transcribe voice to text (if audio)
3. **LangGraph Agent**:
   - Analyze query
   - Choose tools (EHR RAG, web search, vision)
   - Generate response
4. **TTS** → Synthesize response to audio
5. **Frontend** → Display transcript + play audio

---

## 📈 Performance Tips

### For Faster ASR:
- Use GPU: `ASR_DEVICE=cuda`
- Use `float16`: `ASR_COMPUTE_TYPE=float16`

### For Faster LLM:
- Use smaller model: `LLM_MODEL=llama-3.1-8b-instant`
- Reduce RAG results: `k=3` instead of `k=5`

### For Production:
- Enable CORS properly in `backend/app/main.py`
- Use HTTPS
- Set up proper authentication
- Use real FHIR server (not mock data)
- Add rate limiting

---

## 📚 Additional Documentation

- **Full README**: See `README.md`
- **Testing Guide**: See `TESTING_GUIDE.md`
- **Implementation Plan**: See `IMPLEMENTATION_PLAN.md`
- **Setup Details**: See `SETUP_GUIDE.md`

---

## 🆘 Getting Help

**Common Issues:**
1. **API keys not working** → Check `.env` file syntax (no spaces around `=`)
2. **Model conversion fails** → Install ctranslate2: `pip install ctranslate2`
3. **Frontend build fails** → Delete `node_modules` and `npm install` again
4. **Docker issues** → Try `docker-compose down -v` to remove volumes

**Check Logs:**
```bash
# Docker logs
docker-compose logs backend
docker-compose logs frontend

# Local logs
# Backend will show in terminal
# Frontend will show in browser console (F12)
```

---

## ✅ Success Checklist

After setup, verify:

- [ ] Backend responds at http://localhost:8000/api/hello
- [ ] Frontend loads at http://localhost:5173
- [ ] Can select different patients
- [ ] Can type and send text message
- [ ] Can record and send voice message
- [ ] Receives AI response with both text and audio
- [ ] EHR sidebar shows patient data
- [ ] Integration tests pass (`python scripts/test_integration.py`)

---

**🎉 You're all set! Start asking health questions and explore the AI agent capabilities.**

