# ⚡ Quick Workflow Reference - Data Science Focus

**For M.Tech Thesis Presentation**

---

## 🔄 Complete System Flow (One Page)

```
USER INPUT
    │
    ├─ Text Query ──────────────┐
    ├─ Voice (Audio File) ──────┤
    └─ Image/PDF ────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 1: ASR (If Voice Input)           │
│  • Fine-tuned Whisper (medasr-v2-ct2)   │
│  • CTranslate2 optimized                │
│  • Medical terminology specialized       │
│  Output: Transcribed text                │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 2: Safety Check                    │
│  • LLM classification (Llama 3 8B)      │
│  • Categories: SAFE, SOS, HARMFUL       │
│  • Emergency detection                   │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 3: LangGraph Agent                 │
│  • LLM: Groq (Llama 3.1 70B)            │
│  • Multi-step reasoning                 │
│  • Tool selection                       │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 4: Tool Execution                  │
│  ┌───────────────────────────────────┐  │
│  │ RAG Search (Semantic)             │  │
│  │ • ChromaDB vector search          │  │
│  │ • Sentence transformers (384-dim)  │  │
│  │ • Top-k retrieval                 │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ EHR Tools (Structured)             │  │
│  │ • get_latest_lab                   │  │
│  │ • get_medications                  │  │
│  │ • get_conditions                   │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │ Web Search (General Knowledge)     │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 5: Response Synthesis              │
│  • LLM combines tool results            │
│  • Personalized explanation             │
│  • Citations & disclaimers              │
└─────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  STEP 6: TTS (Text-to-Speech)            │
│  • MeloTTS synthesis                    │
│  • Natural voice output                 │
└─────────────────────────────────────────┘
            │
            ▼
    RESPONSE DELIVERY
    • Text + Audio
```

---

## 🔬 Data Science Technologies

### 1. ASR (Automatic Speech Recognition)
- **Model**: Whisper Medium (fine-tuned)
- **Method**: LoRA (Low-Rank Adaptation)
- **Optimization**: CTranslate2
- **Accuracy**: ~95% on medical terms
- **Speed**: 2-3x faster than base

### 2. RAG (Retrieval-Augmented Generation)
- **Vector DB**: ChromaDB (local)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2
- **Dimensions**: 384
- **Search**: Cosine similarity
- **Speed**: ~300-500ms per query

### 3. LLM (Large Language Model)
- **Primary**: Groq (Llama 3.1 70B)
- **Safety**: Groq (Llama 3 8B)
- **Framework**: LangGraph
- **Tools**: 9 specialized tools

### 4. Embeddings
- **Model**: all-MiniLM-L6-v2
- **Size**: 80MB
- **Dimensions**: 384
- **Speed**: ~1000 sentences/sec

---

## 🧪 ML Training Pipeline

```
Stage 1: Data Prep
  Audio + Transcripts → Preprocessing → HuggingFace Dataset

Stage 2: LoRA Training
  Base Whisper → LoRA Adapters → Fine-tuned Model

Stage 3: Conversion
  Merged Model → CTranslate2 → Deployed Model
```

---

## 📊 Key Metrics

| Component | Metric | Value |
|-----------|--------|-------|
| ASR Accuracy | Medical Terms | ~95% |
| ASR Speed | Inference | 2-3x faster |
| RAG Search | Query Time | ~300-500ms |
| LLM Response | Generation | ~2-3s |
| TTS | Synthesis | ~1-2s |
| **Total** | **End-to-End** | **~5-8s** |

---

## 💬 Quick Talking Points

### ASR
> "Fine-tuned Whisper using LoRA on medical speech data. Parameter-efficient training, 2-3x faster with CTranslate2."

### RAG
> "Semantic search using ChromaDB and sentence transformers. 384-dim embeddings, finds relevant info by meaning."

### Agent
> "LangGraph orchestration with Groq LLM. 9 tools for EHR, web search, vision. Multi-step reasoning."

### Training
> "3-stage pipeline: data prep, LoRA fine-tuning, CTranslate2 conversion. Complete ML workflow."

---

## 🎬 Demo Checklist

- [ ] Backend running (Terminal 1 visible)
- [ ] Frontend loaded (http://localhost:5173)
- [ ] Patient selected (Jane Doe)
- [ ] Test query ready: "What medications am I taking?"
- [ ] Backend logs showing tool usage
- [ ] Audio response working

---

## 🎯 Presentation Structure

1. **Opening** (2 min): Project overview
2. **Data Science Deep Dive** (5 min): ASR, RAG, Agent
3. **Architecture** (3 min): System design
4. **Demo** (5 min): Live demonstration
5. **Challenges** (2 min): Solutions
6. **Results** (1 min): Metrics & impact
7. **Q&A** (5 min): Questions

**Total: ~23 minutes**

---

## 🔑 Key Files to Show

1. `backend/app/agents/graph.py` - LangGraph agent
2. `backend/app/services/rag_index.py` - RAG implementation
3. `ml-training/whisper-finetune/` - Training pipeline
4. `backend/app/services/asr_service.py` - ASR service

---

**Quick Reference for Presentation** 📝

