"""Work experience refinement agent for refining job descriptions based on job requirements."""

import json
from typing import Dict, Any, List
from .base_agent import BaseAgent
from prompts import WORK_EXPERIENCE_REFINEMENT_PROMPT


class WorkExperienceRefinementAgent(BaseAgent):
    """Agent for refining work experience descriptions to match job requirements."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Refine work experiences based on job requirements.
        
        Args:
            input_data: Must contain 'work_experiences', 'job_title', 'job_requirements',
                       'requirements_analysis', 'company_analysis'
            
        Returns:
            Dictionary with 'refined_experiences' key containing refined work experiences
        """
        work_experiences = input_data.get("work_experiences", "")
        job_title = input_data.get("job_title", "")
        job_requirements = input_data.get("job_requirements", "")
        requirements_analysis = input_data.get("requirements_analysis", "")
        company_analysis = input_data.get("company_analysis", "")
        
        # If no work experiences, return empty
        if not work_experiences or work_experiences == "記載なし":
            print("[WorkExperienceRefinement] No work experiences to refine")
            return {"refined_experiences": []}
        
        print(f"[WorkExperienceRefinement] Starting refinement for {len(work_experiences)} chars of work experiences")
        
        prompt = self._format_prompt(
            WORK_EXPERIENCE_REFINEMENT_PROMPT,
            work_experiences=work_experiences,
            job_title=job_title,
            job_requirements=job_requirements,
            requirements_analysis=requirements_analysis,
            company_analysis=company_analysis,
        )
        
        print("[WorkExperienceRefinement] Calling LLM...")
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        print(f"[WorkExperienceRefinement] LLM Response received ({len(response_text)} chars)")
        # Print full response for debugging
        print(f"[WorkExperienceRefinement] Full LLM Response:")
        print("=" * 80)
        print(response_text)
        print("=" * 80)
        
        # If no work experiences to refine, return empty
        if not work_experiences or work_experiences == "記載なし":
            return {"refined_experiences": []}
        
        # Parse response - try JSON first, otherwise return empty (let original be used)
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            print(f"[WorkExperienceRefinement] JSON search: start={json_start}, end={json_end}")
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                print(f"[WorkExperienceRefinement] Found JSON: {len(json_str)} chars")
                print(f"[WorkExperienceRefinement] JSON content (first 500 chars): {json_str[:500]}")
                
                parsed_response = json.loads(json_str)
                print(f"[WorkExperienceRefinement] Parsed JSON keys: {parsed_response.keys()}")
                
                refined_experiences = parsed_response.get("work_experiences", [])
                print(f"[WorkExperienceRefinement] Successfully parsed JSON: {len(refined_experiences)} refined experiences")
                
                # Print sample of first refined experience
                if refined_experiences and len(refined_experiences) > 0:
                    first_exp = refined_experiences[0]
                    print(f"[WorkExperienceRefinement] First refined exp keys: {first_exp.keys() if isinstance(first_exp, dict) else 'Not a dict'}")
            else:
                # If no JSON found, return empty list (will use original experiences)
                print("[WorkExperienceRefinement] No JSON found in response")
                refined_experiences = []
        except (json.JSONDecodeError, ValueError) as e:
            # If JSON parse fails, return empty list (will use original experiences)
            print(f"[WorkExperienceRefinement] JSON parse error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            refined_experiences = []
        
        return {
            "refined_experiences": refined_experiences,
        }
