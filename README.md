# AI Agent for Personalised Patient Education

M.Tech Major Project by Aditya Singh Rathore (M24DE3089/G23AI2088)

## 🎯 Project Overview

This project implements an intelligent AI agent that delivers personalized, interactive patient education by synthesizing information from Electronic Health Records (EHRs) and medical images. The system utilizes multimodal AI capabilities including ASR, NLP, Computer Vision, and TTS to provide conversational explanations of complex medical information.

### Key Features

- **🎤 Voice Input**: Medical-grade Whisper ASR (LoRA fine-tuned on medical data)
- **🧠 Intelligent Agent**: LangGraph-powered reasoning with tool orchestration
- **📊 EHR Integration**: Dual-source support (Mock JSON + FHIR Server)
- **🔍 RAG Search**: Semantic search over patient records using ChromaDB
- **👁️ Vision Analysis**: Medical image interpretation (X-rays, MRI, reports)
- **🔊 Voice Output**: High-quality TTS with MeloTTS
- **💬 Modern UI**: React-based conversational interface

---

## 📁 Project Structure

```
mtech-medical-agent/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── agents/            # LangGraph agent & tools
│   │   │   ├── graph.py       # Main agent flow (SOS check → LLM → Tools)
│   │   │   ├── tools.py       # EHR, RAG, web search, vision tools
│   │   │   └── vision_agent.py # Medical image analysis
│   │   ├── api/
│   │   │   └── endpoints.py   # REST API (/chat, /ehr/*, etc.)
│   │   ├── services/
│   │   │   ├── asr_service.py         # Faster-Whisper ASR
│   │   │   ├── tts_service.py         # MeloTTS synthesis
│   │   │   ├── ehr_provider.py        # Abstract EHR interface
│   │   │   ├── ehr_mock_provider.py   # Mock JSON provider
│   │   │   ├── ehr_fhir_provider.py   # FHIR provider
│   │   │   ├── ehr_provider_factory.py # Provider factory
│   │   │   ├── rag_index.py           # ChromaDB RAG system
│   │   │   └── fhir_client.py         # HAPI FHIR client
│   │   └── config.py          # Centralized configuration
│   ├── ct2_models/            # CTranslate2 Whisper model
│   ├── data/
│   │   ├── mock_ehr.json      # Sample patient data (5 patients)
│   │   └── prompt_examples.json # Vision model few-shot examples
│   ├── Dockerfile
│   ├── requirements.txt
│   └── ENV_EXAMPLE            # Environment variables template
├── frontend/                   # React + Vite UI
│   ├── src/
│   │   ├── App.jsx            # Main chat interface
│   │   └── ...
│   ├── Dockerfile
│   └── package.json
├── ml-training/               # Model training pipelines
│   └── whisper-finetune/
│       ├── 1_prepare_dataset.py  # Data preprocessing
│       ├── 2_train_lora.py       # LoRA fine-tuning
│       └── 3_merge_and_convert.py # CT2 conversion
├── docker-compose.yml         # Full stack deployment
└── README.md                  # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose (for full deployment)
- API Keys: Groq, OpenAI (for vision), SerpAPI

### 1. Environment Setup

#### Backend

```bash
cd backend
cp ENV_EXAMPLE .env
# Edit .env with your API keys:
#   GROQ_API_KEY=your_groq_key
#   OPENAI_API_KEY=your_openai_key
#   SERPER_API_KEY=your_serpapi_key
#   EHR_PROVIDER=mock  # or "fhir" or "hybrid"
```

#### Frontend

```bash
cd frontend
cp ENV_EXAMPLE .env
# Edit .env:
#   VITE_API_URL=http://localhost:8000/api
```

### 2. Local Development

#### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

Access the app at http://localhost:5173

### 3. Docker Deployment

```bash
# From project root
docker compose up --build
```

This starts:
- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173
- **HAPI FHIR Server**: http://localhost:8080 (optional)

---

## 🏥 EHR System Architecture

### Provider Pattern

The system uses an **abstract provider interface** allowing seamless switching between data sources:

```python
# In backend/.env
EHR_PROVIDER=mock    # Use local JSON (default)
EHR_PROVIDER=fhir    # Use HAPI FHIR server
EHR_PROVIDER=hybrid  # Try FHIR, fallback to mock
```

### Mock Provider

- **Location**: `backend/data/mock_ehr.json`
- **Patients**: 5 realistic cases with diverse conditions
  - `patient_id_12345`: Type 2 Diabetes, Hypertension (Jane Doe, 42F)
  - `patient_id_67890`: Coronary Artery Disease, CKD (John Smith, 58M)
  - `patient_id_24680`: Asthma, Anemia (Maria Garcia, 35F)
  - `patient_id_13579`: Osteoarthritis, BPH, MCI (Robert Johnson, 67M)
  - `patient_id_98765`: PCOS, Hypothyroidism (Sarah Chen, 29F)

### FHIR Provider

- Connects to HAPI FHIR server (http://localhost:8080/fhir)
- Fetches: Patient, Observation, Condition, MedicationStatement, Procedure
- Converts FHIR resources to unified internal format

### RAG (Retrieval-Augmented Generation)

- **Vector Store**: ChromaDB (local, privacy-preserving)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Indexing**: Automatic hierarchical JSON flattening
- **Search**: Semantic similarity with relevance scoring

---

## 🛠️ API Reference

### Core Endpoints

#### Chat with Agent
```http
POST /api/chat
Content-Type: multipart/form-data

patient_id: string (required)
text_query: string (optional)
audio_file: file (optional, .wav)
image_file: file (optional, medical image/PDF)

Returns: audio/wav (agent's voice response)
```

#### EHR Retrieval

```http
# Get patient summary + JSON
GET /api/ehr/{patient_id}

# Semantic search (RAG)
GET /api/ehr/{patient_id}/search?q=latest+blood+sugar&k=5

# Get labs
GET /api/ehr/{patient_id}/labs
GET /api/ehr/{patient_id}/labs?lab_name=HbA1c

# Get medications
GET /api/ehr/{patient_id}/medications

# Get conditions
GET /api/ehr/{patient_id}/conditions
```

#### System

```http
# List all patients
GET /api/ehr/patients

# Get provider info
GET /api/system/provider

# Seed mock data (Mock provider only)
POST /api/ehr/mock/seed
Body: {"patient_id": "...", "data": {...}}
```

---

## 🔍 Verifying EHR/RAG Functionality

### 1. Test Direct EHR Access

```bash
curl http://localhost:8000/api/ehr/patient_id_12345
```

**Expected**: JSON with `summary`, `data`, and `provider` fields.

### 2. Test RAG Search

```bash
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=HbA1c&k=3"
```

**Expected**: JSON with `results` array containing relevant EHR passages with scores.

### 3. Test in Chat

Ask the agent: **"What was my latest HbA1c and what does it mean?"**

**Backend logs should show**:
```
[TOOL] ehr_rag_search: Searching EHR for patient patient_id_12345 with query: 'HbA1c diabetes blood sugar'
[TOOL] ehr_get_latest_lab: Fetching 'HbA1c' for patient patient_id_12345
```

**Agent response should include**:
- Specific value: "Your HbA1c on 2025-10-20 was 7.2%"
- Explanation in plain language
- Citation: "📊 Data sources used: EHR-RAG, Patient Labs"

### 4. Check Tool Invocation

Review backend console for lines like:
```
Node: call_model
Node: call_tools
Executing tool: ehr_rag_search
Executing tool: ehr_get_latest_lab
```

---

## 🎓 ML Training Pipeline

### Whisper Fine-Tuning

Located in `ml-training/whisper-finetune/`

#### Step 1: Prepare Dataset

```bash
cd ml-training/whisper-finetune
python 1_prepare_dataset.py
```

**Input**: `data/audio/*.wav` + `data/transcripts.json`  
**Output**: `processed_medical_speech_dataset/`

#### Step 2: LoRA Training

```bash
python 2_train_lora.py
```

**Output**: `whisper-medium-medical-lora/` (LoRA adapters)

#### Step 3: Merge & Convert to CTranslate2

```bash
python 3_merge_and_convert.py
```

**Output**: `../../backend/ct2_models/whisper-medium-med/`

### Data Sourcing

Medical speech datasets are scarce due to HIPAA. Recommended sources:
- **MedSpeech**: Public medical speech corpus
- **LibriSpeech Medical**: Medical subset
- **Synthetic**: Use TTS on medical texts
- **Kaggle**: Search "medical speech" or "doctor patient conversation"

---

## 🔐 Security & Privacy

### Data Protection
- **Local RAG**: ChromaDB stores embeddings locally (no cloud uploads)
- **FHIR Auth**: Bearer token support for production servers
- **No PHI Logging**: Patient data not logged to stdout (use structured logging in production)

### Medical Disclaimers
- Agent automatically adds: "⚠️ This is educational information. Please consult your doctor for medical decisions."
- **SOS Node**: Detects emergencies ("I can't breathe") and redirects to emergency services

---

## 📊 Key Technologies

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Backend Framework** | FastAPI | REST API + async support |
| **Agent Orchestration** | LangGraph | Multi-step reasoning & tool use |
| **LLM** | Groq (Llama 3 70B) | Natural language understanding |
| **ASR** | Faster-Whisper (CT2) | Medical speech transcription |
| **TTS** | MeloTTS | Natural voice synthesis |
| **RAG Vector Store** | ChromaDB | Semantic search |
| **Embeddings** | Sentence-Transformers | Text vectorization |
| **FHIR Client** | HAPI FHIR | Healthcare interoperability |
| **Vision** | OpenAI GPT-4 Vision | Medical image analysis |
| **Frontend** | React + Vite | Modern UI |

---

## 🧪 Example Conversations

### Example 1: Lab Result Inquiry

**User** (voice): "What was my latest blood sugar?"

**Agent** (uses `ehr_rag_search` + `ehr_get_latest_lab`):
> Your most recent **HbA1c** test on **October 20, 2025** was **7.2%**. This measures your average blood sugar over the past 2-3 months.
>
> For someone with diabetes, the goal is typically below 7.0%, so yours is slightly elevated. Your doctor noted that improving your diet and medication adherence can help bring this down.
>
> Your **Fasting Glucose** on October 15 was **142 mg/dL**, which is above the target range of 70-130 mg/dL.
>
> 📊 **Data sources used**: EHR-RAG, Patient Labs  
> ⚠️ This is educational information. Please discuss any changes with your doctor.

### Example 2: Medication Question

**User**: "What medications am I taking for my diabetes?"

**Agent** (uses `ehr_get_medications` + `ehr_get_conditions`):
> You're currently taking **Metformin 500mg twice daily** for your **Type 2 Diabetes**.
>
> Metformin works by helping your body use insulin more effectively and reducing the amount of sugar your liver releases. It's best taken with meals to avoid stomach upset.
>
> You're also on **Lisinopril 10mg once daily** for your **Hypertension**, which can be important for protecting your kidneys from diabetes-related damage.
>
> 📊 **Data sources used**: EHR-Medications, EHR-Conditions

### Example 3: General Health Education

**User**: "What is HbA1c?"

**Agent** (uses `web_search` since question is general):
> HbA1c (Hemoglobin A1c) is a blood test that shows your average blood sugar level over the past 2-3 months. It's like a "report card" for diabetes management.
>
> Think of it this way: daily glucose tests are like checking the weather today, while HbA1c is like looking at the climate over a whole season.
>
> For your reference, your latest HbA1c was 7.2% on October 20, 2025.
>
> 📊 **Data sources used**: Web Search, Patient Labs

---

## 🐛 Troubleshooting

### Issue: "Patient ID not found"
**Solution**: Use one of the 5 mock patient IDs or seed new data via `/api/ehr/mock/seed`

### Issue: RAG returns empty results
**Solution**: The patient needs to be indexed first. This happens automatically on first search, but you can force it:
```python
from app.services.ehr_provider_factory import get_ehr_provider
provider = get_ehr_provider()
provider.index_patient("patient_id_12345")
```

### Issue: FHIR connection fails
**Solution**: 
1. Check HAPI FHIR is running: `curl http://localhost:8080/fhir/metadata`
2. Verify `FHIR_BASE_URL` in `.env`
3. Set `EHR_PROVIDER=mock` as fallback

### Issue: ASR model not found
**Solution**: Ensure CT2 model files exist in `backend/ct2_models/whisper-medium-med/`. If missing, run the training pipeline or use base Whisper.

---

## 📈 Future Enhancements

- [ ] Multi-language support (Hindi, Spanish)
- [ ] Real-time vitals integration (IoT devices)
- [ ] Medication interaction checking
- [ ] Appointment scheduling integration
- [ ] Family/caregiver access controls
- [ ] Voice biometrics for authentication
- [ ] Expanded FHIR resource support (Immunizations, AllergyIntolerances)
- [ ] Mobile app (React Native)

---

## 📝 License

This project is for academic purposes (M.Tech Major Project). Commercial use requires appropriate medical software compliance (FDA, CE marking, HIPAA).

---

## 👨‍🎓 Author

**Aditya Singh Rathore**  
M.Tech Student (M24DE3089 / G23AI2088)  
Major Project: AI Agent for Personalised Patient Education

---

## 🙏 Acknowledgments

- **OpenAI Whisper** for ASR foundation
- **LangChain/LangGraph** for agent framework
- **HAPI FHIR** for healthcare interoperability
- **ChromaDB** for vector storage
- **Groq** for fast LLM inference

---

**⚕️ Medical Disclaimer**: This is an educational AI system and NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult qualified healthcare professionals for medical decisions.

