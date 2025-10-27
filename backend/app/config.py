import os
import torch
from dotenv import load_dotenv

load_dotenv()

# --- LLM / Agent Keys ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "YOUR_GROQ_API_KEY_HERE")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "YOUR_SERPER_API_KEY_HERE")

# --- Vision Agent Keys (from your script) ---
# Models
GROQ_VISION_MODEL = "llava-v1.6-34b" # Or "gpt-4-vision-preview"
OPENAI_MODEL = "gpt-4-vision-preview"

# AWS
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "YOUR_AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "YOUR_AWS_SECRET_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "your-medical-images-bucket")

# Kafka
kafka_conf_producer = {
    'bootstrap.servers': os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
    # Add other Kafka config as needed
}
kafka_producer_topic = os.getenv("KAFKA_PRODUCER_TOPIC", "medical_vision_results")

# Custom API Tokens (from your script)
SESSION_TOKEN = os.getenv("SESSION_TOKEN", "YOUR_SESSION_TOKEN")
SESSION_X_API_KEY = os.getenv("SESSION_X_API_KEY", "YOUR_SESSION_X_API_KEY")
AUTHENTICATION_TOKEN = os.getenv("AUTHENTICATION_TOKEN", "YOUR_AUTHENTICATION_TOKEN")

# --- ASR Configuration ---
ASR_MODEL_PATH = os.getenv("ASR_MODEL_PATH", os.path.join(os.path.dirname(__file__), "../ct2_models/medasr-v2-ct2"))
ASR_DEVICE = os.getenv("ASR_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
ASR_COMPUTE_TYPE = os.getenv("ASR_COMPUTE_TYPE", "float16" if torch.cuda.is_available() else "int8")

# --- EHR Provider Configuration ---
# Provider type: "mock" (local JSON), "fhir" (HAPI FHIR server), or "hybrid" (FHIR with mock fallback)
EHR_PROVIDER = os.getenv("EHR_PROVIDER", "mock")

# RAG (Retrieval-Augmented Generation) Settings
RAG_DIR = os.getenv("RAG_DIR", "app/data/rag_index")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))

# FHIR Server Configuration
FHIR_BASE_URL = os.getenv("FHIR_BASE_URL", "http://localhost:8080/fhir")
FHIR_BEARER_TOKEN = os.getenv("FHIR_BEARER_TOKEN", "")
FHIR_TIMEOUT = int(os.getenv("FHIR_TIMEOUT", "15"))