# ⚡ QUICK RUN COMMANDS - Copy & Paste Ready

## 🔑 **STEP 1: Add API Keys (REQUIRED FIRST!)**

```bash
nano /home/uwcuser/nltk_data/mtech-medical-agent/backend/.env
```

Add these lines (replace with your actual keys):
```
GROQ_API_KEY=your_actual_groq_key_here
SERPER_API_KEY=your_actual_serper_key_here
OPENAI_API_KEY=your_actual_openai_key_here
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## 📦 **STEP 2: Install Dependencies (ONE TIME ONLY)**

### Backend Dependencies
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
pip install -r requirements.txt
```

### Frontend Dependencies
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/frontend
npm install
```

---

## 🚀 **STEP 3: Run the System**

### Terminal 1 - Start Backend
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Start Frontend
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/frontend
npm run dev
```

### Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🧪 **STEP 4: Quick Tests**

### Test Backend is Running
```bash
curl http://localhost:8000/
```

### Test EHR Data Access
```bash
curl http://localhost:8000/api/ehr/patient_id_12345 | python3 -m json.tool
```

### Test Chat (Text Query)
```bash
curl -X POST http://localhost:8000/api/chat \
  -F "patient_id=patient_id_12345" \
  -F "text_query=What medications am I taking?" \
  -F "return_json=true" | python3 -m json.tool
```

---

## 🛑 **STOP Everything**

```bash
# Press Ctrl+C in both terminal windows
# Or run these commands:
pkill -f uvicorn
pkill -f vite
```

---

## 🔄 **Restart if Needed**

```bash
# Terminal 1
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
cd /home/uwcuser/nltk_data/mtech-medical-agent/frontend
npm run dev
```

---

## 📋 **5 Demo Patient IDs**

Use these for testing:
- `patient_id_12345` - Jane Doe (Diabetes, Hypertension)
- `patient_id_67890` - John Smith (Heart Disease)
- `patient_id_24680` - Maria Garcia (Asthma)
- `patient_id_13579` - Robert Johnson (Arthritis)
- `patient_id_98765` - Sarah Chen (PCOS)

---

## 💬 **Sample Questions to Ask**

1. "What was my latest HbA1c result?"
2. "What medications am I currently taking?"
3. "Tell me about my diabetes diagnosis"
4. "What do my recent blood pressure readings show?"
5. "Can you explain my blood pressure medication?"

---

## 🐛 **Quick Troubleshooting**

### "Module not found" errors
```bash
cd /home/uwcuser/nltk_data/mtech-medical-agent/backend
pip install -r requirements.txt --force-reinstall
```

### Frontend won't connect
```bash
# Make sure backend is running first
curl http://localhost:8000/

# Check frontend .env
cat /home/uwcuser/nltk_data/mtech-medical-agent/frontend/.env
```

### CUDA out of memory
```bash
# Edit backend/.env and change:
# ASR_DEVICE=cpu
# ASR_COMPUTE_TYPE=int8
nano /home/uwcuser/nltk_data/mtech-medical-agent/backend/.env
```

---

## ✅ **Success Indicators**

### Backend Startup (Terminal 1)
You should see:
```
✅ ASR Service: Loaded model from ct2_models/medasr-v2-ct2
✅ EHR Service: Mock database loaded with 5 patients
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Frontend Startup (Terminal 2)
You should see:
```
VITE v5.x.x ready in XXX ms
➜  Local:   http://localhost:5173/
```

### Chat Query (Backend Logs)
You should see:
```
[TOOL] ehr_rag_search: Searching EHR for patient...
[TOOL] ehr_get_medications: Fetching medications...
```

---

**That's it! Your system should now be running.** 🎉

Open http://localhost:5173 in your browser and start chatting!




