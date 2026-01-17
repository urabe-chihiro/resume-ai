"""Resume generation agent."""

from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import RESUME_GENERATION_PROMPT


class ResumeGenerationAgent(BaseAgent):
    """Agent for generating resume content."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate resume content.
        
        Args:
            input_data: Must contain 'user_input', 'job_requirements', 'company_analysis',
                       'requirements_analysis', 'structure_plan'
            
        Returns:
            Dictionary with 'resume_markdown' key containing the generated resume
        """
        user_input = input_data.get("user_input", "")
        job_requirements = input_data.get("job_requirements", "")
        company_analysis = input_data.get("company_analysis", "")
        requirements_analysis = input_data.get("requirements_analysis", "")
        structure_plan = input_data.get("structure_plan", "")
        
        prompt = self._format_prompt(
            RESUME_GENERATION_PROMPT,
            user_input=user_input,
            job_requirements=job_requirements,
            company_analysis=company_analysis,
            requirements_analysis=requirements_analysis,
            structure_plan=structure_plan,
        )
        
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            resume_markdown = response.content
        else:
            resume_markdown = str(response)
        
        return {
            "resume_markdown": resume_markdown,
        }
