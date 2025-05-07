from fastapi import APIRouter, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from typing import List
import os

from app.services.resume_service import ResumeService
from app.models.resume_model import ResumeResponse, Resume
from app.services.gemini_resume_service import GeminiResumeService
from app.services.gemini_direct_service import GeminiDirectService  # Import the new service

router = APIRouter(prefix="/api/v1/resume", tags=["Resume Extraction"])

# Create singleton instances of the services
resume_service = ResumeService()
gemini_resume_service = GeminiResumeService()
gemini_direct_service = GeminiDirectService()


def get_resume_service() -> ResumeService:
    return resume_service


def get_gemini_resume_service() -> GeminiResumeService:
    return gemini_resume_service


def get_gemini_direct_service() -> GeminiDirectService:
    return gemini_direct_service


@router.post("/extract", response_model=ResumeResponse, summary="Extract data from resume (standard)")
async def extract_resume(
    file: UploadFile = File(...),
    service: ResumeService = Depends(get_resume_service)
):
    """
    Extract structured data from a resume file (PDF) using the standard extraction method.

    - **file**: Resume file (currently only PDF format is supported).

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


@router.post("/gemini-extract", response_model=ResumeResponse, summary="Extract resume data using Gemini (enhanced)")
async def extract_resume_with_gemini(
    file: UploadFile = File(...),
    service: GeminiResumeService = Depends(get_gemini_resume_service)
):
    """
    Extract structured data from a resume file (PDF) using Gemini for enhanced extraction.

    - **file**: Resume file (currently only PDF format is supported).

    Returns a structured JSON with all extracted fields, potentially enhanced by Gemini.
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

        # Extract data using the Gemini-enhanced service
        resume_data = await service.extract_resume_data(file_content, file_extension)

        # Validate extraction success (you might want to adjust this based on Gemini's output)
        if not service.validate_extraction(resume_data):
            return ResumeResponse(
                success=False,
                message="Unable to extract sufficient data from the resume using Gemini. Please check file quality and format.",
                data=resume_data
            )

        return ResumeResponse(
            success=True,
            message="Resume data extracted successfully using Gemini",
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
            message=f"An error occurred during Gemini-enhanced extraction: {str(e)}",
            data=None
        )

@router.post(
    "/extract-gemini-direct",
    response_model=ResumeResponse,
    summary="Extract resume data from a PDF file using Gemini (direct)"
)
async def extract_resume_gemini_direct(
    file: UploadFile = File(...),
    service: GeminiDirectService = Depends(get_gemini_direct_service)
):
    """
    Upload a PDF file and extract structured resume data using Gemini directly.

    - **file**: The uploaded resume file in PDF format.

    Returns a structured JSON with all extracted fields, extracted directly by Gemini.
    """
    try:
        resume_data = await service.extract_data_from_pdf_file(file)
        return ResumeResponse(
            success=True,
            message="Resume data extracted successfully from file using Gemini (direct)",
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
            message=f"An unexpected error occurred during Gemini direct extraction: {str(e)}",
            data=None
        )


@router.get("/supported-formats", response_model=List[str])
async def get_supported_formats():
    """
    Get a list of supported file formats for resume extraction
    """
    return ["pdf"]