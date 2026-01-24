"""User input data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class PersonalProject(BaseModel):
    """Personal project entry."""
    
    title: str = Field(..., description="Project title")
    description: str = Field(..., description="Project description")
    technologies: List[str] = Field(default_factory=list, description="Technologies used")
    url: Optional[str] = Field(None, description="Project URL (GitHub, portfolio, etc.)")
    date: Optional[str] = Field(None, description="Project completion date or period")


class WorkExperience(BaseModel):
    """Work experience entry."""
    
    company_name: str = Field(..., description="Company name")
    position: str = Field(..., description="Job position/title")
    period: str = Field(..., description="Employment period (e.g., 2020年4月～2023年3月)")
    description: Optional[str] = Field(None, description="Job description and achievements")


class UserInput(BaseModel):
    """User input data model."""
    
    # Basic Information
    name: str = Field(..., description="Full name")
    residence: Optional[str] = Field(None, description="Residence (e.g., 神奈川県在住)")
    job_title: Optional[str] = Field(None, description="Job title (e.g., バックエンドエンジニア)")
    years_of_experience: Optional[str] = Field(None, description="Years of experience (e.g., 15年間)")
    appeal_points: Optional[str] = Field(None, description="Appeal points (strengths and key selling points)")
    
    # Skills
    programming_languages: List[str] = Field(default_factory=list, description="Programming languages")
    frameworks: List[str] = Field(default_factory=list, description="Frameworks and libraries")
    testing_tools: List[str] = Field(default_factory=list, description="Testing tools")
    design_tools: List[str] = Field(default_factory=list, description="Design tools")
    
    # Work Experience
    work_experiences: List[WorkExperience] = Field(default_factory=list, description="Work experience history")
    
    # Personal Projects
    personal_projects: List[PersonalProject] = Field(default_factory=list, description="Personal development projects")
    portfolio_url: Optional[str] = Field(None, description="Portfolio or GitHub URL")

