"""Requirements extraction agent."""

from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import REQUIREMENTS_EXTRACTION_PROMPT


class RequirementsExtractionAgent(BaseAgent):
    """Agent for extracting requirements from job postings."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract requirements from job posting.
        
        Args:
            input_data: Must contain 'job_description' and 'company_analysis'
            
        Returns:
            Dictionary with 'requirements' key containing extracted requirements
        """
        job_description = input_data.get("job_description", "")
        company_analysis = input_data.get("company_analysis", "")
        
        prompt = self._format_prompt(
            REQUIREMENTS_EXTRACTION_PROMPT,
            job_description=job_description,
            company_analysis=company_analysis,
        )
        
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            requirements = response.content
        else:
            requirements = str(response)
        
        return {
            "requirements": requirements,
            "job_description": job_description,
            "company_analysis": company_analysis,
        }
