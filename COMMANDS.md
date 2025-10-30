# 📋 Complete Command Reference

## 🎯 Quick Reference

This document contains ALL commands you'll need to setup, run, test, and maintain the Medical AI Agent.

---

## 🚀 ONE-COMMAND SETUP

### Automated Setup (Recommended)
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent
./setup.sh
```

This interactive script will:
1. Check prerequisites
2. Setup environment files
3. Convert ASR model
4. Let you choose Docker or Local setup
5. Run integration tests
6. Display next steps

---

## 📦 Manual Setup Commands

### 1. Initial Setup

```bash
# Navigate to project
cd /home/uwcuser/nltk_data/mtech-medical-agent

# Create environment files
cp backend/ENV_EXAMPLE backend/.env
cp frontend/ENV_EXAMPLE frontend/.env

# Edit backend/.env to add your API keys
nano backend/.env
# Add: GROQ_API_KEY, SERPER_API_KEY
```

### 2. Convert ASR Model to CTranslate2

```bash
# Install conversion dependencies (if not already installed)
pip install ctranslate2>=3.20.0 transformers>=4.35.0 torch

# Run conversion
cd ml-training
./convert_to_ct2.sh

# Or manually:
python convert_to_ct2.py

# Verify conversion
ls -la ../backend/ct2_models/medasr-v2-ct2/
# Should see: model.bin, config.json, vocabulary.json, etc.
```

---

## 🐳 Docker Commands

### Start with Docker Compose

```bash
# Build and start all services (backend, frontend, FHIR)
docker-compose up --build

# Or run in background
docker-compose up -d --build

# Access:
# Frontend:  http://localhost:5173
# Backend:   http://localhost:8000/api
# API Docs:  http://localhost:8000/docs
# FHIR:      http://localhost:8080/fhir
```

### Docker Management

```bash
# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f hapi-fhir

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Restart services
docker-compose restart

# Rebuild a specific service
docker-compose up -d --build backend
```

### Docker Cleanup

```bash
# Remove all containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Clean Docker system
docker system prune -a

# Remove specific images
docker rmi medical-agent-backend
docker rmi medical-agent-frontend
```

---

## 💻 Local Development Commands

### Backend

```bash
# Setup
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run with specific host/port
uvicorn app.main:app --reload --host 127.0.0.1 --port 8080

# Run without reload (production-like)
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Setup
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Install new dependencies
npm install react-icons
npm install --save-dev tailwindcss
```

### FHIR Server (HAPI FHIR)

```bash
# Run standalone HAPI FHIR
docker run -p 8080:8080 \
  -e HAPI_FHIR_ALLOW_EXTERNAL_REFERENCES=true \
  -e HAPI_FHIR_ALLOW_MULTIPLE_DELETE=true \
  hapiproject/hapi:latest

# Run in background
docker run -d -p 8080:8080 \
  --name hapi-fhir \
  -e HAPI_FHIR_ALLOW_EXTERNAL_REFERENCES=true \
  hapiproject/hapi:latest

# Stop FHIR server
docker stop hapi-fhir
docker rm hapi-fhir
```

---

## 🧪 Testing Commands

### Integration Tests

```bash
# Run full integration test suite
cd scripts
python test_integration.py

# With custom API URL
API_URL=http://localhost:8000/api python test_integration.py
```

### Manual API Testing

```bash
# Test API connectivity
curl http://localhost:8000/api/hello

# Test EHR provider info
curl http://localhost:8000/api/system/provider

# Test patient retrieval
curl http://localhost:8000/api/ehr/patient_id_12345 | jq

# Test RAG search
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=5" | jq

# Test lab results
curl http://localhost:8000/api/ehr/patient_id_12345/labs | jq

# Test medications
curl http://localhost:8000/api/ehr/patient_id_12345/medications | jq

# Test conditions
curl http://localhost:8000/api/ehr/patient_id_12345/conditions | jq

# Test TTS
curl -X POST http://localhost:8000/api/test/synthesize \
  -F "text=Hello world" \
  --output test_tts.wav

# Test ASR (need an audio file)
curl -X POST http://localhost:8000/api/test/transcribe \
  -F "audio_file=@path/to/audio.wav"

# Test full chat (text input, JSON response)
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What medications am I taking?" \
  -F "return_json=true" | jq

# Test chat with image upload
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=Analyze this medical image" \
  -F "image_file=@path/to/image.jpg" \
  -F "return_json=true" | jq
```

### Mock EHR Seeding

```bash
# Seed a new patient
curl -X POST http://localhost:8000/api/ehr/mock/seed \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "patient_test_001",
    "data": {
      "personal_info": {
        "name": "Test Patient",
        "age": 45,
        "gender": "Female"
      },
      "conditions": [
        {"name": "Hypertension", "diagnosed_on": "2024-01-15"}
      ],
      "medications": [
        {"name": "Lisinopril", "dosage": "10mg", "frequency": "Once daily"}
      ],
      "recent_labs": []
    }
  }' | jq
```

### Browser Testing

```bash
# Open frontend
xdg-open http://localhost:5173  # Linux
open http://localhost:5173      # macOS
start http://localhost:5173     # Windows

# Open API docs
xdg-open http://localhost:8000/docs
```

---

## 🔍 Debugging Commands

### View Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Follow logs for all services
docker-compose logs -f

# View last 100 lines
docker-compose logs --tail=100 backend

# Local development logs are in terminal output
```

### Check Service Status

```bash
# Check if ports are in use
lsof -i :8000  # Backend
lsof -i :5173  # Frontend
lsof -i :8080  # FHIR

# Check Docker containers
docker ps

# Check Docker images
docker images | grep medical-agent
```

### Verify File Structure

```bash
# Check CT2 model
ls -la backend/ct2_models/medasr-v2-ct2/

# Check environment files
cat backend/.env
cat frontend/.env

# Check if all components exist
ls -la backend/app/agents/
ls -la backend/app/services/
ls -la frontend/src/components/
ls -la frontend/src/hooks/
```

### Python Environment

```bash
# Check installed packages
pip list | grep -E "fastapi|langchain|faster-whisper|chromadb"

# Install missing packages
pip install faster-whisper chromadb sentence-transformers

# Verify imports
python -c "from faster_whisper import WhisperModel; print('OK')"
python -c "import chromadb; print('OK')"
```

---

## 🛠️ Maintenance Commands

### Update Dependencies

```bash
# Backend
cd backend
pip install --upgrade -r requirements.txt

# Frontend
cd frontend
npm update
```

### Clean and Rebuild

```bash
# Backend - Clean Python cache
cd backend
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# Frontend - Clean and reinstall
cd frontend
rm -rf node_modules
npm install

# Docker - Clean rebuild
docker-compose down -v
docker system prune -a
docker-compose up --build
```

### Database Management

```bash
# Clear RAG index
rm -rf backend/app/data/rag_index/*

# Re-index patients (will happen automatically on first search)
curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=test&k=1"
```

---

## 📊 Performance Monitoring

### Check System Resources

```bash
# Docker stats
docker stats

# Check CPU/Memory usage
htop

# Check disk usage
df -h
du -sh backend/ct2_models/
du -sh backend/app/data/rag_index/
```

### Benchmark Performance

```bash
# Time a chat request
time curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What are my conditions?" \
  -F "return_json=true" > /dev/null

# RAG search timing
time curl "http://localhost:8000/api/ehr/patient_id_12345/search?q=diabetes&k=5" > /dev/null
```

---

## 🚨 Emergency Commands

### Kill All Processes

```bash
# Kill backend (if stuck)
pkill -f "uvicorn app.main:app"

# Kill frontend
pkill -f "vite"

# Kill Docker containers
docker-compose down

# Force kill all medical-agent containers
docker ps | grep medical-agent | awk '{print $1}' | xargs docker kill
```

### Reset Everything

```bash
# Complete reset
cd /home/uwcuser/nltk_data/mtech-medical-agent

# Stop all services
docker-compose down -v
pkill -f uvicorn
pkill -f vite

# Clean Docker
docker system prune -a

# Clean Python cache
find backend -type d -name "__pycache__" -exec rm -rf {} +

# Clean node modules
rm -rf frontend/node_modules

# Clear RAG index
rm -rf backend/app/data/rag_index/*

# Start fresh
./setup.sh
```

---

## 📝 Environment Variables Reference

### Backend `.env`

```bash
# LLM
GROQ_API_KEY=your_key_here
LLM_MODEL=llama-3.1-70b-versatile

# Search
SERPER_API_KEY=your_key_here

# EHR
EHR_PROVIDER=mock  # or fhir, hybrid
FHIR_BASE_URL=http://localhost:8080/fhir

# RAG
RAG_DIR=app/data/rag_index
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# ASR
ASR_MODEL_PATH=ct2_models/medasr-v2-ct2
ASR_DEVICE=cuda  # or cpu
ASR_COMPUTE_TYPE=float16  # or int8

# AWS (optional)
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=us-east-1
S3_BUCKET_NAME=your_bucket
```

### Frontend `.env`

```bash
VITE_API_URL=http://localhost:8000/api
```

---

## 🎓 Common Workflows

### Development Workflow

```bash
# 1. Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# 2. In new terminal, start frontend
cd frontend
npm run dev

# 3. Make changes, auto-reload happens

# 4. Test changes
curl http://localhost:8000/api/hello
# Or open http://localhost:5173
```

### Testing New Features

```bash
# 1. Make code changes
# 2. Restart backend (if needed)
# 3. Test with curl or browser
# 4. Run integration tests
python scripts/test_integration.py
```

### Deployment Preparation

```bash
# 1. Build production frontend
cd frontend
npm run build

# 2. Build Docker images
docker-compose build

# 3. Test production build
docker-compose up

# 4. Run tests
python scripts/test_integration.py
```

---

## 🎯 Most Used Commands Summary

```bash
# Quick start (Docker)
./setup.sh

# Manual Docker start
docker-compose up --build

# Local backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Local frontend
cd frontend && npm run dev

# Run tests
python scripts/test_integration.py

# Test API
curl http://localhost:8000/api/hello

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

---

**💡 Tip:** Bookmark this file for quick reference during development!
