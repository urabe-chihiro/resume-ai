"""Company analysis agent."""

from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import COMPANY_ANALYSIS_PROMPT


class CompanyAnalysisAgent(BaseAgent):
    """Agent for analyzing company information and job postings."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze company and job posting.
        
        Args:
            input_data: Must contain 'company_info' and 'job_description'
            
        Returns:
            Dictionary with 'analysis' key containing the analysis
        """
        company_info = input_data.get("company_info", "")
        job_description = input_data.get("job_description", "")
        
        prompt = self._format_prompt(
            COMPANY_ANALYSIS_PROMPT,
            company_info=company_info,
            job_description=job_description,
        )
        
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            analysis = response.content
        else:
            analysis = str(response)
        
        return {
            "analysis": analysis,
            "company_info": company_info,
            "job_description": job_description,
        }
