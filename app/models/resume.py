from pydantic import BaseModel
from typing import List


class ResumeData(BaseModel):
    name: str = "Not Present"
    email: str = "Not Present"
    phone: str = "Not Present"
    linkedin: str = "Not Present"
    github: str = "Not Present"
    skills: List[str] = ["Not Present"]
    education: List[str] = ["Not Present"]
    experience: List[str] = ["Not Present"]
    projects: List[str] = ["Not Present"]
    achievements: List[str] = ["Not Present"]
    interview_topics: List[str] = ["Not Present"]
