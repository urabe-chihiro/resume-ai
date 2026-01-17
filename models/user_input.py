"""User input data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class WorkExperience(BaseModel):
    """Work experience entry."""
    
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job position/title")
    start_date: str = Field(..., description="Start date")
    end_date: Optional[str] = Field(None, description="End date (None if current)")
    description: str = Field(..., description="Job description and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")


class Education(BaseModel):
    """Education entry."""
    
    institution: str = Field(..., description="Educational institution name")
    degree: str = Field(..., description="Degree or qualification")
    field: str = Field(..., description="Field of study")
    graduation_date: str = Field(..., description="Graduation date")
    gpa: Optional[str] = Field(None, description="GPA if applicable")


class Skill(BaseModel):
    """Skill entry."""
    
    category: str = Field(..., description="Skill category (e.g., Programming, Languages)")
    items: List[str] = Field(..., description="List of skills in this category")


class UserInput(BaseModel):
    """User input data model."""
    
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    summary: Optional[str] = Field(None, description="Professional summary")
    work_experiences: List[WorkExperience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: List[Skill] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
