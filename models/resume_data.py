"""Resume data models."""

from typing import List
from pydantic import BaseModel, Field


class ResumeSection(BaseModel):
    """Resume section."""
    
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Section content in markdown")
    order: int = Field(..., description="Display order")


class ResumeData(BaseModel):
    """Complete resume data."""
    
    name: str = Field(..., description="Candidate name")
    contact_info: str = Field(..., description="Contact information")
    sections: List[ResumeSection] = Field(..., description="Resume sections")
    
    def to_markdown(self) -> str:
        """Convert resume to markdown format."""
        markdown_parts = [
            f"# {self.name}\n",
            f"{self.contact_info}\n",
            "---\n",
        ]
        
        sorted_sections = sorted(self.sections, key=lambda x: x.order)
        for section in sorted_sections:
            markdown_parts.append(f"## {section.title}\n")
            markdown_parts.append(f"{section.content}\n")
            markdown_parts.append("\n")
        
        return "\n".join(markdown_parts)
