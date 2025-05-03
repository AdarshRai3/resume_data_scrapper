from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.resume import ResumeData
from app.services.parser_service import parse_resume

router = APIRouter()

@router.post("/extract", response_model=ResumeData)
async def extract_resume_data(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    try:
        content = await file.read()
        data = parse_resume(content)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resume parsing failed: {str(e)}")
