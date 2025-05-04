from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional


class Education(BaseModel):
    institution: str = Field(default="Not Present")
    location: str = Field(default="Not Present")
    degree: str = Field(default="Not Present")
    cgpa: str = Field(default="Not Present")
    period: str = Field(default="Not Present")


class Experience(BaseModel):
    company: str = Field(default="Not Present")
    position: str = Field(default="Not Present")
    location: str = Field(default="Not Present")
    period: str = Field(default="Not Present")
    responsibilities: List[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str = Field(default="Not Present")
    technologies: List[str] = Field(default_factory=list)
    date: str = Field(default="Not Present")
    description: List[str] = Field(default_factory=list)


class Resume(BaseModel):
    name: str = Field(default="Not Present")
    email: EmailStr = Field(default="Not Present")
    phone: str = Field(default="Not Present")
    linkedin: str = Field(default="Not Present")
    github: str = Field(default="Not Present")
    skills: List[str] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    experience: List[Experience] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
    interview_topics: List[str] = Field(default_factory=list)


class ResumeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Resume] = None