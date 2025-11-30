# 📚 Documentation Index - Medical AI Agent

Welcome! This index will guide you to the right documentation based on your needs.

---

## 🚀 Getting Started (New Users)

**Start here if you're setting up the project for the first time:**

1. **[QUICK_START.md](QUICK_START.md)** ⭐ **START HERE**
   - Fastest way to get running
   - Prerequisites checklist
   - Docker vs Local setup
   - First-time configuration
   - **Estimated time: 10-15 minutes**

2. **[setup.sh](setup.sh)** - Automated Setup Script
   - Run `./setup.sh` for interactive setup
   - Handles everything automatically
   - Checks prerequisites
   - Converts models
   - Starts services

3. **[COMMANDS.md](COMMANDS.md)** - Command Reference
   - Every command you'll need
   - Docker commands
   - Testing commands
   - Debugging commands
   - **Bookmark this for daily use!**

---

## 📖 Understanding the Project

**Read these to understand what was built and how it works:**

1. **[README.md](README.md)** - Complete Project Documentation
   - Project overview
   - Architecture details
   - Feature descriptions
   - Technology stack
   - Deployment guide
   - **Read this after setup**

2. **[SUMMARY.md](SUMMARY.md)** - Implementation Summary
   - What was built (all phases)
   - Files created/modified
   - Before/after comparisons
   - Success metrics
   - Future enhancements
   - **Great for presentations!**

3. **[IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** - Development Roadmap
   - Original development plan
   - Priority order
   - Time estimates
   - Technical decisions
   - **For understanding development process**

---

## 🧪 Testing the System

**Use these guides to test and verify everything works:**

1. **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Comprehensive Testing
   - Unit tests
   - Integration tests
   - Manual testing procedures
   - EHR verification
   - RAG testing
   - Agent testing
   - **Essential for validation**

2. **[scripts/test_integration.py](scripts/test_integration.py)** - Automated Tests
   - Run `python scripts/test_integration.py`
   - Tests all components
   - Beautiful output
   - Pass/fail summary
   - **Run this after setup!**

---

## 🔧 Technical Deep Dives

**Detailed technical documentation for specific components:**

### Backend

1. **[backend/app/agents/](backend/app/agents/)**
   - `graph.py` - LangGraph agent definition
   - `tools.py` - All agent tools (EHR, search, vision)
   - Agent system prompts
   - Tool selection logic

2. **[backend/app/services/](backend/app/services/)**
   - `asr_service.py` - Speech recognition (Whisper)
   - `tts_service.py` - Text-to-speech (MeloTTS)
   - `ehr_provider.py` - EHR abstraction
   - `ehr_mock_provider.py` - Mock EHR implementation
   - `ehr_fhir_provider.py` - FHIR integration
   - `rag_index.py` - RAG/ChromaDB system
   - `vision_agent.py` - Medical image analysis

3. **[backend/app/api/endpoints.py](backend/app/api/endpoints.py)**
   - All API endpoints
   - Request/response formats
   - Error handling

4. **[backend/ENV_EXAMPLE](backend/ENV_EXAMPLE)**
   - All environment variables explained
   - Configuration options
   - API key setup

### Frontend

1. **[frontend/src/App.jsx](frontend/src/App.jsx)**
   - Main application component
   - Chat interface
   - Patient management
   - File upload

2. **[frontend/src/components/](frontend/src/components/)**
   - `PatientSelector.jsx` - Patient switcher
   - `FileUploadZone.jsx` - File upload UI
   - `TranscriptPanel.jsx` - Message display
   - `EHRSidebar.jsx` - Patient data sidebar
   - `LoadingIndicator.jsx` - Loading states

3. **[frontend/src/hooks/](frontend/src/hooks/)**
   - `usePatient.js` - Patient state management
   - `useChat.js` - Chat state management

### ML Training

1. **[ml-training/convert_to_ct2.py](ml-training/convert_to_ct2.py)**
   - Converts Hugging Face model to CTranslate2
   - Configurable quantization
   - Model validation

2. **[ml-training/convert_to_ct2.sh](ml-training/convert_to_ct2.sh)**
   - Shell wrapper for conversion
   - Easy to run

---

## 🔍 Finding What You Need

### By Task

| What you want to do | Read this |
|---------------------|-----------|
| **Set up the project** | [QUICK_START.md](QUICK_START.md) or run `./setup.sh` |
| **Run the application** | [COMMANDS.md](COMMANDS.md) → "Quick start" section |
| **Test everything works** | [TESTING_GUIDE.md](TESTING_GUIDE.md) or run `python scripts/test_integration.py` |
| **Understand the architecture** | [README.md](README.md) → "System Architecture" |
| **Configure environment** | [backend/ENV_EXAMPLE](backend/ENV_EXAMPLE) + [QUICK_START.md](QUICK_START.md) |
| **Debug issues** | [COMMANDS.md](COMMANDS.md) → "Debugging Commands" |
| **Deploy to production** | [README.md](README.md) → "Deployment" + [docker-compose.yml](docker-compose.yml) |
| **Add new features** | [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) → "Future Enhancements" |
| **Understand what was built** | [SUMMARY.md](SUMMARY.md) |
| **See all commands** | [COMMANDS.md](COMMANDS.md) |

### By Component

| Component | Documentation |
|-----------|---------------|
| **ASR (Speech Recognition)** | [backend/app/services/asr_service.py](backend/app/services/asr_service.py) + [ml-training/](ml-training/) |
| **TTS (Speech Synthesis)** | [backend/app/services/tts_service.py](backend/app/services/tts_service.py) |
| **EHR System** | [backend/app/services/ehr_*.py](backend/app/services/) + [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| **RAG Search** | [backend/app/services/rag_index.py](backend/app/services/rag_index.py) + [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| **LangGraph Agent** | [backend/app/agents/graph.py](backend/app/agents/graph.py) |
| **Agent Tools** | [backend/app/agents/tools.py](backend/app/agents/tools.py) |
| **Vision Analysis** | [backend/app/agents/vision_agent.py](backend/app/agents/vision_agent.py) |
| **API Endpoints** | [backend/app/api/endpoints.py](backend/app/api/endpoints.py) + API Docs at http://localhost:8000/docs |
| **Frontend UI** | [frontend/src/](frontend/src/) |
| **FHIR Integration** | [backend/app/services/fhir_client.py](backend/app/services/fhir_client.py) + [backend/app/services/ehr_fhir_provider.py](backend/app/services/ehr_fhir_provider.py) |
| **Docker Setup** | [docker-compose.yml](docker-compose.yml) + [Dockerfile (backend/frontend)](.) |

### By Role

#### **Developers** (Making Changes)
1. [QUICK_START.md](QUICK_START.md) - Setup
2. [COMMANDS.md](COMMANDS.md) - Daily commands
3. [README.md](README.md) - Architecture
4. Code files in `backend/` and `frontend/`

#### **QA/Testers** (Testing)
1. [QUICK_START.md](QUICK_START.md) - Setup
2. [TESTING_GUIDE.md](TESTING_GUIDE.md) - Test procedures
3. [scripts/test_integration.py](scripts/test_integration.py) - Run tests
4. [COMMANDS.md](COMMANDS.md) - Manual testing commands

#### **DevOps** (Deployment)
1. [docker-compose.yml](docker-compose.yml) - Container orchestration
2. [backend/ENV_EXAMPLE](backend/ENV_EXAMPLE) - Configuration
3. [COMMANDS.md](COMMANDS.md) - Docker commands
4. [README.md](README.md) - Deployment section

#### **Product Managers** (Understanding Features)
1. [SUMMARY.md](SUMMARY.md) - What was built
2. [README.md](README.md) - Features overview
3. [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Roadmap

#### **End Users** (Using the App)
1. [QUICK_START.md](QUICK_START.md) → "Using the Application"
2. Open http://localhost:5173 after setup
3. Try sample questions in the UI

---

## 🎯 Recommended Reading Order

### For First-Time Setup (30 minutes)
1. ✅ [QUICK_START.md](QUICK_START.md) (10 min) - Get running
2. ✅ Run `python scripts/test_integration.py` (5 min) - Verify it works
3. ✅ Try the UI at http://localhost:5173 (10 min) - Hands-on experience
4. ✅ Skim [README.md](README.md) (5 min) - Understand architecture

### For Understanding the System (1 hour)
1. [SUMMARY.md](SUMMARY.md) (15 min) - Overview of what was built
2. [README.md](README.md) (30 min) - Deep dive into architecture
3. [TESTING_GUIDE.md](TESTING_GUIDE.md) (15 min) - How to verify components

### For Daily Development (Ongoing)
1. Bookmark [COMMANDS.md](COMMANDS.md) - Always needed
2. Keep [TESTING_GUIDE.md](TESTING_GUIDE.md) handy
3. Refer to code files as needed

---

## 📂 Complete File Tree

```
mtech-medical-agent/
├── 📖 DOCUMENTATION
│   ├── INDEX.md                    [THIS FILE] - Documentation index
│   ├── QUICK_START.md              ⭐ Start here for setup
│   ├── README.md                   📚 Complete project docs
│   ├── SUMMARY.md                  📋 Implementation summary
│   ├── IMPLEMENTATION_PLAN.md      🎯 Development roadmap
│   ├── TESTING_GUIDE.md            🧪 Testing procedures
│   ├── COMMANDS.md                 💻 All commands reference
│   └── setup.sh                    🚀 Automated setup script
│
├── 🔧 BACKEND
│   ├── app/
│   │   ├── main.py                 FastAPI app entry
│   │   ├── config.py               Configuration management
│   │   ├── agents/
│   │   │   ├── graph.py            LangGraph agent
│   │   │   ├── tools.py            Agent tools (EHR, search, vision)
│   │   │   └── vision_agent.py     Medical image analysis
│   │   ├── api/
│   │   │   └── endpoints.py        All API endpoints
│   │   ├── services/
│   │   │   ├── asr_service.py      Speech recognition
│   │   │   ├── tts_service.py      Text-to-speech
│   │   │   ├── ehr_*.py            EHR providers
│   │   │   ├── rag_index.py        RAG/ChromaDB
│   │   │   └── fhir_client.py      FHIR API client
│   │   └── data/
│   │       ├── mock_ehr.json       5 demo patients
│   │       └── rag_index/          Vector database
│   ├── ct2_models/                 CTranslate2 models
│   ├── requirements.txt            Python dependencies
│   ├── ENV_EXAMPLE                 Environment template
│   └── Dockerfile                  Backend container
│
├── 🎨 FRONTEND
│   ├── src/
│   │   ├── App.jsx                 Main app component
│   │   ├── main.jsx                React entry
│   │   ├── index.css               Tailwind styles
│   │   ├── components/
│   │   │   ├── PatientSelector.jsx
│   │   │   ├── FileUploadZone.jsx
│   │   │   ├── TranscriptPanel.jsx
│   │   │   ├── EHRSidebar.jsx
│   │   │   └── LoadingIndicator.jsx
│   │   └── hooks/
│   │       ├── usePatient.js
│   │       └── useChat.js
│   ├── tailwind.config.js          Tailwind config
│   ├── postcss.config.js           PostCSS config
│   ├── package.json                npm dependencies
│   ├── ENV_EXAMPLE                 Environment template
│   └── Dockerfile                  Frontend container
│
├── 🤖 ML TRAINING
│   ├── medasr-v2/                  Fine-tuned Whisper model
│   ├── convert_to_ct2.py           Model conversion script
│   ├── convert_to_ct2.sh           Conversion wrapper
│   └── whisper-finetune/           Fine-tuning code (optional)
│
├── 🧪 TESTING
│   └── scripts/
│       └── test_integration.py     Integration tests
│
└── 🐳 DEPLOYMENT
    └── docker-compose.yml          Container orchestration
```

---

## 🆘 Getting Help

### Common Questions

**Q: Where do I start?**
A: Run `./setup.sh` or read [QUICK_START.md](QUICK_START.md)

**Q: How do I test if it's working?**
A: Run `python scripts/test_integration.py` or see [TESTING_GUIDE.md](TESTING_GUIDE.md)

**Q: What commands do I need?**
A: Check [COMMANDS.md](COMMANDS.md)

**Q: How does the architecture work?**
A: Read [README.md](README.md) → "System Architecture"

**Q: Where are the API keys configured?**
A: In `backend/.env` (see [backend/ENV_EXAMPLE](backend/ENV_EXAMPLE))

**Q: How do I add a new patient?**
A: POST to `/api/ehr/mock/seed` (see [TESTING_GUIDE.md](TESTING_GUIDE.md))

**Q: How do I debug errors?**
A: Check [COMMANDS.md](COMMANDS.md) → "Debugging Commands"

**Q: Can I deploy this?**
A: Yes! See [README.md](README.md) → "Deployment" section

### Still Need Help?

1. Check logs: `docker-compose logs -f` or terminal output
2. Verify setup: `python scripts/test_integration.py`
3. Test API: `curl http://localhost:8000/api/hello`
4. Review error messages and check relevant documentation

---

## 🎉 Quick Actions

```bash
# 🚀 Setup everything
./setup.sh

# 🐳 Start with Docker
docker-compose up --build

# 💻 Start locally
# Terminal 1:
cd backend && source venv/bin/activate && uvicorn app.main:app --reload
# Terminal 2:
cd frontend && npm run dev

# 🧪 Test
python scripts/test_integration.py

# 📖 Read docs
cat README.md
cat QUICK_START.md

# 💡 Get help
curl http://localhost:8000/api/hello
docker-compose logs -f
```

---

**Happy developing! 🚀**

*Last updated: October 27, 2025*
