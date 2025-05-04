from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import os

from app.services.resume_service import ResumeService
from app.models.resume_model import ResumeResponse, Resume

router = APIRouter(prefix="/api/v1/resume", tags=["Resume Extraction"])

# Create a singleton instance of ResumeService
resume_service = ResumeService()


def get_resume_service() -> ResumeService:
    return resume_service


@router.post("/extract", response_model=ResumeResponse, summary="Extract data from resume")
async def extract_resume(
    file: UploadFile = File(...),
    service: ResumeService = Depends(get_resume_service)
):
    """
    Extract structured data from a resume file (PDF)
    
    - **file**: Resume file (currently only PDF format is supported)
    
    Returns a structured JSON with all extracted fields.
    """
    try:
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1][1:].lower()
        if file_extension != "pdf":
            return ResumeResponse(
                success=False,
                message=f"Unsupported file format: {file_extension}. Only PDF is currently supported.",
                data=None
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract data
        resume_data = await service.extract_resume_data(file_content, file_extension)
        
        # Validate extraction success
        if not service.validate_extraction(resume_data):
            return ResumeResponse(
                success=False,
                message="Unable to extract sufficient data from the resume. Please check file quality and format.",
                data=resume_data
            )
        
        return ResumeResponse(
            success=True,
            message="Resume data extracted successfully",
            data=resume_data
        )
        
    except ValueError as e:
        return ResumeResponse(
            success=False,
            message=str(e),
            data=None
        )
    except Exception as e:
        return ResumeResponse(
            success=False,
            message=f"An error occurred during extraction: {str(e)}",
            data=None
        )


@router.get("/supported-formats", response_model=List[str])
async def get_supported_formats():
    """
    Get a list of supported file formats for resume extraction
    """
    return ["pdf"]