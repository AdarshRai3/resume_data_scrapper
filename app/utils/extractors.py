import re
from typing import List, Dict

SECTION_KEYWORDS = {
    "education": ["education", "academic background", "qualifications"],
    "experience": ["experience", "work experience", "professional experience", "internship"],
    "projects": ["projects", "technical projects", "personal projects"],
    "achievements": ["achievements", "awards", "honors", "certifications"],
    "interview_topics": ["interview topics", "interview questions"],
    "skills": ["skills", "technical skills", "tools & technologies"]
}

def extract_name(lines: List[str]) -> str:
    for line in lines:
        low = line.lower()
        if not line.strip():
            continue
        if "resume" in low or "curriculum vitae" in low or line.strip().lower() == "cv":
            continue
        if re.search(r'\d', line) or "@" in line:
            continue
        return line.strip()
    return "Not Present"

def extract_email(text: str) -> str:
    match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    return match.group(0) if match else "Not Present"

def extract_phone(text: str) -> str:
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})', text)
    return match.group(0) if match else "Not Present"

def extract_linkedin(text: str) -> str:
    match = re.search(r'(https?://)?(www\.)?linkedin\.com/[^\s,;]+', text, re.IGNORECASE)
    return match.group(0) if match else "Not Present"

def extract_github(text: str) -> str:
    match = re.search(r'(https?://)?(www\.)?github\.com/[^\s,;]+', text, re.IGNORECASE)
    return match.group(0) if match else "Not Present"

def extract_skills(section_data: Dict[str, List[str]]) -> List[str]:
    skills_section = section_data.get("skills", [])
    if skills_section == ["Not Present"]:
        return ["Not Present"]

    joined_text = " ".join(skills_section)
    potential_skills = re.split(r'[,\n•|;]', joined_text)
    cleaned_skills = [skill.strip() for skill in potential_skills if skill.strip()]
    
    return cleaned_skills if cleaned_skills else ["Not Present"]

def extract_education(section_data: Dict[str, List[str]]) -> List[str]:
    education_lines = section_data.get("education", [])
    education = []

    degree_pattern = re.compile(
        r'(BACHELOR|MASTER|B\.?TECH|M\.?TECH|BCA|MCA|B\.?SC|M\.?SC|BE|B\.?E\.?|ME|M\.?E\.?)',
        re.IGNORECASE
    )
    institution_keywords = ["institute", "university", "college", "school", "academy"]

    for line in education_lines:
        lower_line = line.lower()
        if degree_pattern.search(line):
            education.append(line)
        elif re.search(r'\d{4}', line):  # Matches year patterns
            education.append(line)
        elif any(word in lower_line for word in institution_keywords):
            education.append(line)

    return education if education else ["Not Present"]


def extract_experience(section_data: Dict[str, List[str]]) -> List[str]:
    experience_lines = section_data.get("experience", [])
    filtered = []

    # List of job-related keywords and action verbs for job responsibilities
    job_keywords = [
        "developer", "intern", "engineer", "consultant", "analyst", "manager",
        "lead", "architect", "qa", "tester", "administrator", "contributor", "specialist", "designer"
    ]
    
    action_keywords = [
        "developed", "built", "designed", "implemented", "led", "maintained",
        "managed", "automated", "tested", "supported", "resolved", "collaborated", "worked on"
    ]

    # Date patterns to match various date formats
    date_patterns = [
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec)[a-z]*[\s\-.,]*\d{2,4}',  # Matches months like "Jan 2024"
        r'\[\d{4}\s*[–-]\s*(\d{4}|present)\]',  # Matches years like [2020-2023]
        r'\d{4}\s*[–-]\s*(\d{4}|present)',  # Matches year ranges like 2020-2023
        r'\(\d{4}\)',  # Matches years inside parentheses (2024)
        r'\b\d{4}\b',  # Matches years as standalone (2024)
        r'\b(?:present|current)\b',  # Matches the term "present" or "current"
    ]
    
    # Check each line for job-related keywords, action keywords, or date patterns
    for line in experience_lines:
        lower_line = line.lower()
        
        # Check if the line contains job-related keywords
        if any(keyword in lower_line for keyword in job_keywords):
            filtered.append(line)
        
        # Check if the line mentions action verbs related to job responsibilities
        elif any(keyword in lower_line for keyword in action_keywords):
            filtered.append(line)
        
        # Check if the line contains a date pattern (e.g., date range or 'present')
        elif any(re.search(pattern, lower_line) for pattern in date_patterns):
            filtered.append(line)

    # Clean up: Remove any line with fewer than 3 words
    filtered = [line for line in filtered if len(line.split()) > 2]

    # If no experience data found, return "Not Present"
    return filtered if filtered else ["Not Present"]


def split_into_sections(lines: List[str]) -> Dict[str, List[str]]:
    section_indices = {}
    for section, keywords in SECTION_KEYWORDS.items():
        section_indices[section] = None
        for i, line in enumerate(lines):
            if any(kw in line.lower() for kw in keywords):
                section_indices[section] = i
                break

    sorted_sections = sorted(
        [(idx, sec) for sec, idx in section_indices.items() if idx is not None],
        key=lambda x: x[0]
    )

    sections_content = {}
    for i, (idx, section) in enumerate(sorted_sections):
        start = idx + 1
        end = sorted_sections[i + 1][0] if i + 1 < len(sorted_sections) else len(lines)
        section_lines = [lines[j].strip() for j in range(start, end) if lines[j].strip()]
        sections_content[section] = section_lines or ["Not Present"]

    for section in SECTION_KEYWORDS:
        sections_content.setdefault(section, ["Not Present"])

    return sections_content
