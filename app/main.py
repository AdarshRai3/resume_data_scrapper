from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.resume import router as resume_router
import os
from app.core.config import settings

app = FastAPI(
    title="Resume Analyzer API",
    description="API to upload and analyze resumes using PDF parsing and NLP",
    version="1.0.0",
    docs_url="/docs",          
    redoc_url="/redoc",        
    openapi_url="/openapi.json"  
)

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

# Register router
app.include_router(resume_router, prefix="/api/v1/resume", tags=["Resume"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)