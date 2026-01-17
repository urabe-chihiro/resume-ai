"""Resume structure agent."""

from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import RESUME_STRUCTURE_PROMPT


class ResumeStructureAgent(BaseAgent):
    """Agent for planning resume structure."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Plan optimal resume structure.
        
        Args:
            input_data: Must contain 'user_experience', 'job_requirements', 'company_analysis'
            
        Returns:
            Dictionary with 'structure_plan' key containing the plan
        """
        user_experience = input_data.get("user_experience", "")
        job_requirements = input_data.get("job_requirements", "")
        company_analysis = input_data.get("company_analysis", "")
        
        prompt = self._format_prompt(
            RESUME_STRUCTURE_PROMPT,
            user_experience=user_experience,
            job_requirements=job_requirements,
            company_analysis=company_analysis,
        )
        
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            structure_plan = response.content
        else:
            structure_plan = str(response)
        
        return {
            "structure_plan": structure_plan,
            "user_experience": user_experience,
            "job_requirements": job_requirements,
            "company_analysis": company_analysis,
        }
