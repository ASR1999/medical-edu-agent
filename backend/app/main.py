from fastapi import FastAPI
from app.api.endpoints import router as api_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="M.Tech Medical AI Agent",
    description="API for the personalized patient education agent."
)

# --- CORS Middleware ---
# Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, lock this to your React app's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "Medical Agent API is running"}