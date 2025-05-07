from app.extractors.pdf_extractor import PDFExtractor
from app.models.resume_model import Resume


class ResumeService:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
    
    async def extract_resume_data(self, file_content: bytes, file_extension: str) -> Resume:
        """
        Extract data from resume file based on file type
        
        Args:
            file_content: The binary content of the uploaded file
            file_extension: The file extension (pdf, docx, etc.)
            
        Returns:
            Resume object with extracted data
        """
        if file_extension.lower() == 'pdf':
            return self.pdf_extractor.extract_from_pdf(file_content)
        else:
            # For now, we only support PDF. Can extend later.
            raise ValueError(f"Unsupported file format: {file_extension}")
    
    def validate_extraction(self, resume: Resume) -> bool:
        """
        Validate if the extraction was successful
        
        Args:
            resume: The extracted Resume object
            
        Returns:
            True if extraction was reasonably successful
        """
        # Check if at least some critical fields were extracted
        if resume.name == "Not Present" and resume.email == "Not Present" and not resume.skills:
            return False
        
        return True