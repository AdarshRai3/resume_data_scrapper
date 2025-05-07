import os
import json
import tempfile
import re
import google.generativeai as genai
from fastapi import UploadFile
from app.models.resume_model import Resume

class GeminiDirectService:
    def __init__(self):
        self.gemini_api_key = "AIzaSyBeP3MxXlDGJFlYxQnfRiGkjXbJCVE7ZxI"
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not provided.")
        genai.configure(api_key=self.gemini_api_key)
        self.genai_client = genai.GenerativeModel(model_name="models/gemini-2.0-flash")

    async def extract_data_from_pdf_file(self, file: UploadFile) -> Resume:
        temp_file_path = ""
        try:
            # Read PDF content
            pdf_content = await file.read()

            # Save to a temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(pdf_content)
                temp_file_path = temp_file.name

            # Upload to Gemini
            uploaded_file = genai.upload_file(path=temp_file_path, mime_type="application/pdf")

            # Prompt
            prompt = """
            Analyze the attached PDF and extract the following details in raw JSON format (without markdown or explanation) and access the pdf and select the topic for interview and put them in interview_topics field. If any field is missing, use "Not Present".

            JSON Format:
            {
              "name": "Not Present",
              "email": "Not Present",
              "phone": "Not Present",
              "linkedin": "Not Present",
              "github": "Not Present",
              "skills": [],
              "education": [
                {
                  "institution": "Not Present",
                  "location": "Not Present",
                  "degree": "Not Present",
                  "cgpa": "Not Present",
                  "period": "Not Present"
                }
              ],
              "experience": [
                {
                  "company": "Not Present",
                  "position": "Not Present",
                  "location": "Not Present",
                  "period": "Not Present",
                  "responsibilities": []
                }
              ],
              "projects": [
                {
                  "name": "Not Present",
                  "technologies": [],
                  "date": "Not Present",
                  "description": []
                }
              ],
              "achievements": [],
              "interview_topics": []
            }
            """

            # Get Gemini response
            response = await self.genai_client.generate_content_async([prompt, uploaded_file])
            gemini_output = response.text.strip()
            print("Raw Gemini Output:\n", gemini_output)

            # Extract JSON block
            json_match = re.search(r"\{.*\}", gemini_output, re.DOTALL)
            if not json_match:
                raise ValueError("Could not extract JSON from Gemini output.")

            cleaned_json = json_match.group(0)

            # Parse and return
            resume_data = json.loads(cleaned_json)
            return Resume(**resume_data)

        except Exception as e:
            raise ValueError(f"An error occurred during Gemini processing: {e}") from e

        finally:
            # Clean up
            if temp_file_path and os.path.exists(temp_file_path):
                os.remove(temp_file_path)
