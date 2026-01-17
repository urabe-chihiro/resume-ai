"""Job requirements and company info data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class CompanyInfo(BaseModel):
    """Company information."""
    
    name: str = Field(..., description="Company name")
    industry: Optional[str] = Field(None, description="Industry sector")
    size: Optional[str] = Field(None, description="Company size")
    culture: Optional[str] = Field(None, description="Company culture description")
    values: List[str] = Field(default_factory=list, description="Company values")


class JobRequirements(BaseModel):
    """Job requirements data model."""
    
    job_title: str = Field(..., description="Job title")
    company_info: CompanyInfo = Field(..., description="Company information")
    job_description: str = Field(..., description="Full job description")
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
