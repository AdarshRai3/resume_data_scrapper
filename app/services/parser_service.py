import fitz  # PyMuPDF
from app.utils.extractors import (
    extract_name,
    extract_email,
    extract_phone,
    extract_linkedin,
    extract_github,
    extract_skills,
    extract_education,
    extract_experience,
    split_into_sections,
)
from app.models.resume import ResumeData

def extract_text_and_lines_from_pdf(file) -> tuple[str, list[str]]:
    try:
        doc = fitz.open(stream=file, filetype="pdf")
        text = "\n".join(page.get_text() for page in doc)
        doc.close()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return text, lines
    except Exception:
        return "", []

def parse_resume(file) -> ResumeData:
    text, lines = extract_text_and_lines_from_pdf(file)
    sections = split_into_sections(lines)

    return ResumeData(
        name=extract_name(lines),
        email=extract_email(text),
        phone=extract_phone(text),
        linkedin=extract_linkedin(text),
        github=extract_github(text),
        skills=extract_skills(sections),
        education=extract_education(sections),
        experience=extract_experience(sections),
        projects=sections.get("projects", ["Not Present"]),
        achievements=sections.get("achievements", ["Not Present"]),
        interview_topics=sections.get("interview_topics", ["Not Present"]),
    )
