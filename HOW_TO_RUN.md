# 🚀 COMPLETE GUIDE: How to Run Your Medical AI Agent System

**Created for M.Tech Major Project by Aditya Singh Rathore**

---

## 📌 **IMPORTANT NOTES**

1. **ASR Training Code**: The training pipeline in `ml-training/whisper-finetune/` is for demonstration purposes. The model `medasr-v2` is already trained and converted to CT2 format.

2. **EHR System**: The system uses **Mock JSON EHR** by default (`backend/data/mock_ehr.json`). The FHIR implementation is available but optional - you can demonstrate both approaches to examiners.

3. **End-to-End Functionality**: All components work together seamlessly - ASR → Agent → RAG → EHR → LLM → TTS.

---

## 🎯 **SYSTEM OVERVIEW**

Your project has **5 Mock Patients** ready to use:
- `patient_id_12345` - Jane Doe, 42F (Type 2 Diabetes, Hypertension)
- `patient_id_67890` - John Smith, 58M (Coronary Artery Disease)
- `patient_id_24680` - Maria Garcia, 35F (Asthma, Anemia)
- `patient_id_13579` - Robert Johnson, 67M (Osteoarthritis)
- `patient_id_98765` - Sarah Chen, 29F (PCOS, Hypothyroidism)

---

## ⚙️ **STEP 1: Configure API Keys**

You need 3 API keys (2 required, 1 optional):

### 1.1 Edit Backend Environment File

```bash
nano /home/uwcuser/nltk_data/mtech-medical-agent/backend/.env
```

Add these keys:

```env
# === REQUIRED API Keys ===
GROQ_API_KEY=your_groq_api_key_here
SERPER_API_KEY=your_serper_api_key_here

# === OPTIONAL (for vision analysis) ===
OPENAI_API_KEY=your_openai_api_key_here

# === EHR Provider (USE MOCK for demonstration) ===
EHR_PROVIDER=mock

# === ASR Model (Already configured) ===
ASR_MODEL_PATH=ct2_models/medasr-v2-ct2
ASR_DEVICE=cuda
ASR_COMPUTE_TYPE=float16

# === RAG Settings (Already configured) ===
RAG_DIR=app/data/rag_index
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

**How to get API keys:**
- **Groq API**: https://console.groq.com/keys (Free tier available)
- **Serper API**: https://serper.dev/api-key (Free tier: 2500 searches)
- **OpenAI API**: https://platform.openai.com/api-keys (Optional, for vision analysis)

### 1.2 Frontend Environment (Already Configured)

```bash
cat /home/uwcuser/nltk_data/mtech-medical-agent/frontend/.env
```

Should show:
```
VITE_API_URL=http://localhost:8000/api
```

---

## 📦 **STEP 2: Install Dependencies**

### 2.1 Backend Dependencies

```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
pip install -r requirements.txt
```

**Estimated time**: 5-10 minutes

**Key packages being installed:**
- FastAPI, uvicorn
- LangGraph, LangChain
- faster-whisper (ASR)
- MeloTTS (Text-to-Speech)
- ChromaDB (RAG vector store)
- sentence-transformers (Embeddings)

### 2.2 Frontend Dependencies

```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/frontend
npm install
```

**Estimated time**: 2-3 minutes

---

## 🔍 **STEP 3: Verify ASR Model**

The ASR model should already be converted. Let's verify:

```bash
ls -lh /home/uwcuser/nltk_data/mtech-medical-agent/backend/ct2_models/medasr-v2-ct2/
```

**Expected output:**
```
-rw-r--r-- config.json
-rw-r--r-- model.bin (large file, ~1-3 GB)
-rw-r--r-- vocabulary.json
```

✅ **If files exist**: Model is ready!

❌ **If files missing**: Run conversion:
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/ml-training
chmod +x convert_to_ct2.sh
./convert_to_ct2.sh
```

---

## 🚀 **STEP 4: Run the Application**

You have 2 options:

### **Option A: Local Development (Recommended for Demo)**

**Terminal 1 - Backend:**
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Wait for:**
```
✅ ASR Service: Loaded model from ct2_models/medasr-v2-ct2 on cuda (float16)
✅ EHR Service: Mock database loaded with 5 patients
✅ Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 - Frontend:**
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/frontend
npm run dev
```

**Wait for:**
```
VITE v5.x.x ready in XXX ms
➜  Local:   http://localhost:5173/
```

---

### **Option B: Docker Compose (Production-like)**

```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent
docker compose up --build
```

**This starts 3 services:**
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- HAPI FHIR Server: http://localhost:8080

---

## 🧪 **STEP 5: Test the System**

### Test 1: Backend Health Check

```bash
curl http://localhost:8000/
```

**Expected:**
```json
{"status": "Medical Agent API is running"}
```

### Test 2: Get Patient Data

```bash
curl http://localhost:8000/api/ehr/patient_id_12345 | python3 -m json.tool
```

**Expected:** JSON with patient data (Jane Doe)

### Test 3: RAG Search

```bash
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=3" | python3 -m json.tool
```

**Expected:** Relevant EHR chunks about diabetes

### Test 4: Full Chat Test

```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What medications am I taking?" \
  -F "return_json=true" | python3 -m json.tool
```

**Expected:** JSON with:
- `transcript`: Agent's text response
- `audio`: Base64 audio
- `sources`: Tools used

---

## 🌐 **STEP 6: Use the Frontend**

### 6.1 Open Browser

Navigate to: **http://localhost:5173**

### 6.2 Test Questions

Try these queries to demonstrate end-to-end functionality:

**Query 1: Lab Results**
```
What was my latest HbA1c result?
```
**Agent should:**
- Use `ehr_rag_search` and `ehr_get_latest_lab` tools
- Respond: "Your HbA1c on 2025-10-20 was 7.2%..."
- Show sources used

**Query 2: Medications**
```
What medications am I currently taking?
```
**Agent should:**
- Use `ehr_get_medications` tool
- List Metformin and Lisinopril
- Explain what each does

**Query 3: General Education**
```
What is HbA1c and why is it important?
```
**Agent should:**
- Use `web_search` for general info
- Use `ehr_get_latest_lab` for patient-specific data
- Provide personalized explanation

**Query 4: Voice Input** (if microphone available)
- Click microphone icon
- Ask: "Tell me about my diabetes"
- System transcribes with ASR → Agent responds → TTS plays audio

---

## 📊 **STEP 7: Demonstrate to Examiners**

### What to Show:

#### 1. **Multimodal Input/Output**
- ✅ Text input → Text + Audio output
- ✅ Voice input (ASR) → Text + Audio output
- ✅ Image upload (optional if OpenAI API available)

#### 2. **EHR Integration**
- ✅ Show `backend/data/mock_ehr.json` (5 patients)
- ✅ Explain Mock vs FHIR provider pattern
- ✅ Demo switching `EHR_PROVIDER=fhir` (optional)

#### 3. **RAG System**
```bash
# Show RAG indexing
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=blood pressure&k=5"
```
- ✅ Explain ChromaDB vector storage
- ✅ Show semantic search over EHR

#### 4. **Agent Tool Use**
- ✅ Backend logs show: `[TOOL] ehr_rag_search`, `[TOOL] ehr_get_medications`
- ✅ Explain LangGraph orchestration
- ✅ Show agent reasoning flow

#### 5. **Medical ASR (Training Pipeline)**
- ✅ Show code: `ml-training/whisper-finetune/`
- ✅ Explain: "Model already trained and converted"
- ✅ Demo: Converted CT2 model in `backend/ct2_models/`

---

## 🔧 **STEP 8: Troubleshooting**

### Issue 1: "ASR model not found"
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/ml-training
./convert_to_ct2.sh
```

### Issue 2: "CUDA out of memory"
Edit `backend/.env`:
```env
ASR_DEVICE=cpu
ASR_COMPUTE_TYPE=int8
```

### Issue 3: Frontend can't connect
Check backend is running:
```bash
curl http://localhost:8000/
```

Check frontend .env:
```bash
cat frontend/.env
# Should have: VITE_API_URL=http://localhost:8000/api
```

### Issue 4: Agent doesn't use tools
Check backend logs for:
```
[TOOL] ehr_rag_search: Searching EHR...
[TOOL] ehr_get_latest_lab: Fetching...
```

If missing:
- Verify Groq API key is valid
- Check LLM model is `llama-3.1-70b-versatile` (larger models work better)

---

## 📈 **Architecture Highlights for Examiners**

### 1. **Modular Service Architecture**
```
backend/app/
├── agents/          # LangGraph agent logic
├── api/             # FastAPI endpoints
└── services/        # ASR, TTS, EHR, RAG services
```

### 2. **Provider Pattern for EHR**
```python
# backend/app/services/ehr_provider_factory.py
EHR_PROVIDER = "mock"  # or "fhir" or "hybrid"
```
- Mock: Local JSON (fast, privacy-preserving)
- FHIR: HAPI FHIR server (industry standard)
- Hybrid: FHIR with mock fallback

### 3. **RAG with ChromaDB**
- Local vector store (no cloud)
- Semantic search over EHR
- Privacy-preserving

### 4. **LangGraph Agent Flow**
```
User Query → ASR → SOS Check → LLM Reasoning → Tool Selection → Tool Execution → Response Generation → TTS
```

---

## 🎓 **Key Points for Defense**

1. **Medical ASR**: Fine-tuned Whisper on medical terminology (medasr-v2)
2. **EHR Integration**: Dual-source (Mock + FHIR) with abstraction layer
3. **RAG**: Semantic search over patient records using ChromaDB
4. **Agent**: LangGraph orchestrates 7+ tools for intelligent retrieval
5. **Privacy**: Local RAG, no PHI logging
6. **Scalability**: Docker Compose for deployment
7. **Safety**: SOS detection node, medical disclaimers

---

## ✅ **Quick Start Checklist**

Before demo:

- [ ] API keys added to `backend/.env`
- [ ] Dependencies installed (backend + frontend)
- [ ] ASR model exists in `backend/ct2_models/medasr-v2-ct2/`
- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:5173)
- [ ] Test query works: "What medications am I taking?"
- [ ] Backend logs show tool usage: `[TOOL] ehr_get_medications`
- [ ] Audio response plays correctly

---

## 🆘 **Emergency Commands**

### Stop Everything
```bash
# Kill backend
pkill -f uvicorn

# Kill frontend
pkill -f vite

# Or for Docker
docker compose down
```

### Restart Fresh
```bash
# Terminal 1
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
cd /home/uwcuser/nltk_data/mtech-medical-agent/frontend
npm run dev
```

### Check Logs
```bash
# Backend terminal shows tool usage
# Frontend browser console (F12) shows API calls
```

---

## 📚 **Additional Resources**

- **Full Documentation**: `README.md`
- **API Documentation**: http://localhost:8000/docs (when backend running)
- **Testing Guide**: `TESTING_GUIDE.md`
- **Implementation Plan**: `IMPLEMENTATION_PLAN.md`

---

## 🎉 **You're Ready!**

Your Medical AI Agent system is production-ready for demonstration. The architecture showcases:

✅ **Advanced ML**: Medical ASR, Vision AI, LLM reasoning  
✅ **Healthcare IT**: EHR integration (Mock + FHIR standards)  
✅ **Modern AI**: RAG, LangGraph, multi-agent systems  
✅ **Full Stack**: FastAPI backend, React frontend  
✅ **Privacy**: Local-first RAG, no cloud data leakage  

**Good luck with your M.Tech project defense!** 🎓🩺🤖

---

**Aditya Singh Rathore** (M24DE3089 / G23AI2088)  
M.Tech Major Project: AI Agent for Personalised Patient Education




