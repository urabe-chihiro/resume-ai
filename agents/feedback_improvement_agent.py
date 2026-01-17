"""Feedback improvement agent."""

from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import FEEDBACK_IMPROVEMENT_PROMPT


class FeedbackImprovementAgent(BaseAgent):
    """Agent for improving resume based on feedback."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Improve resume based on feedback.
        
        Args:
            input_data: Must contain 'current_resume', 'feedback', 'user_input', 'job_requirements'
            
        Returns:
            Dictionary with 'improved_resume' key containing the improved resume
        """
        current_resume = input_data.get("current_resume", "")
        feedback = input_data.get("feedback", "")
        user_input = input_data.get("user_input", "")
        job_requirements = input_data.get("job_requirements", "")
        
        prompt = self._format_prompt(
            FEEDBACK_IMPROVEMENT_PROMPT,
            current_resume=current_resume,
            feedback=feedback,
            user_input=user_input,
            job_requirements=job_requirements,
        )
        
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            improved_resume = response.content
        else:
            improved_resume = str(response)
        
        return {
            "improved_resume": improved_resume,
        }
