"""Summary generation agent for creating professional job summary."""

from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import SUMMARY_GENERATION_PROMPT


class SummaryGenerationAgent(BaseAgent):
    """Agent for generating professional job summary based on appeal points, skills, and personal projects."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate professional summary.
        
        Args:
            input_data: Must contain 'appeal_points', 'work_experiences', 'skills', 'personal_projects',
                       'company_analysis', 'requirements_analysis'
            
        Returns:
            Dictionary with 'summary' key containing the generated summary
        """
        appeal_points = input_data.get("appeal_points", "")
        work_experiences = input_data.get("work_experiences", "")
        programming_languages = input_data.get("programming_languages", "")
        frameworks = input_data.get("frameworks", "")
        testing_tools = input_data.get("testing_tools", "")
        design_tools = input_data.get("design_tools", "")
        personal_projects = input_data.get("personal_projects", "")
        company_analysis = input_data.get("company_analysis", "")
        requirements_analysis = input_data.get("requirements_analysis", "")
        
        prompt = self._format_prompt(
            SUMMARY_GENERATION_PROMPT,
            appeal_points=appeal_points,
            work_experiences=work_experiences,
            programming_languages=programming_languages,
            frameworks=frameworks,
            testing_tools=testing_tools,
            design_tools=design_tools,
            personal_projects=personal_projects,
            company_analysis=company_analysis,
            requirements_analysis=requirements_analysis,
        )
        
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            summary = response.content
        else:
            summary = str(response)
        
        return {
            "summary": summary,
        }
