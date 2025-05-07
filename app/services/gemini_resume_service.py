import os
import google.generativeai as genai
from app.extractors.pdf_extractor import PDFExtractor
from app.models.resume_model import Resume
import json  

class GeminiResumeService:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.gemini_api_key = "AIzaSyBeP3MxXlDGJFlYxQnfRiGkjXbJCVE7ZxI"  # Remember to use environment variable in production
        self.genai_client = genai.GenerativeModel(model_name="gemini-2.0-flash")

    async def extract_resume_data(self, file_content: bytes, file_extension: str) -> Resume:
        if file_extension.lower() == 'pdf':
            initial_extraction = self.pdf_extractor.extract_from_pdf(file_content)
            refined_data = await self._refine_with_gemini(initial_extraction)
            return refined_data
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

    async def _refine_with_gemini(self, initial_data: Resume) -> Resume:
        prompt = f"""
        ...
        """
        try:
            response = await self.genai_client.generate_content_async(prompt)
            gemini_output = response.text.strip()
            try:
                refined_json = json.loads(gemini_output)
                return Resume(**refined_json)
            except json.JSONDecodeError as e:
                print(f"Error decoding Gemini JSON: {e}")
                return initial_data
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return initial_data

    def validate_extraction(self, resume: Resume) -> bool:
        if resume.name == "Not Present" and resume.email == "Not Present" and not resume.skills:
            return False
        return True