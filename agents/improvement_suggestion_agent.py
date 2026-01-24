"""Improvement suggestion agent for suggesting resume improvements."""

import json
from typing import Dict, Any, List
from .base_agent import BaseAgent
from prompts import IMPROVEMENT_SUGGESTION_PROMPT


class ImprovementSuggestionAgent(BaseAgent):
    """Agent for suggesting improvements to the resume based on missing information."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate improvement suggestions based on resume data and job requirements.
        
        Args:
            input_data: Must contain 'resume_data', 'job_title', 'job_description'
            
        Returns:
            Dictionary with 'suggestions' list and 'prompt_text'
        """
        resume_data = input_data.get("resume_data", {})
        job_title = input_data.get("job_title", "")
        job_description = input_data.get("job_description", "")
        
        # Format resume data for prompt
        resume_data_text = self._format_resume_data(resume_data)
        
        print("[ImprovementSuggestion] Analyzing resume and generating improvement suggestions...")
        
        prompt = self._format_prompt(
            IMPROVEMENT_SUGGESTION_PROMPT,
            resume_data=resume_data_text,
            job_title=job_title,
            job_description=job_description,
        )
        
        print("[ImprovementSuggestion] Calling LLM...")
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        print(f"[ImprovementSuggestion] LLM Response received ({len(response_text)} chars)")
        
        # Parse response
        suggestions = []
        prompt_text = "職務経歴書に追加したい補足情報や経験を入力してください。"
        
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                parsed_response = json.loads(json_str)
                suggestions = parsed_response.get("suggestions", [])
                prompt_text = parsed_response.get("prompt_text", prompt_text)
                print(f"[ImprovementSuggestion] Successfully parsed {len(suggestions)} suggestions")
            else:
                print("[ImprovementSuggestion] No JSON found in response")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[ImprovementSuggestion] JSON parse error: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
        
        return {
            "suggestions": suggestions,
            "prompt_text": prompt_text,
        }
    
    def _format_resume_data(self, resume_data: Dict[str, Any]) -> str:
        """Format resume data for the prompt."""
        parts = []
        
        if resume_data.get("name"):
            parts.append(f"氏名: {resume_data['name']}")
        
        if resume_data.get("job_title"):
            parts.append(f"職種: {resume_data['job_title']}")
        
        if resume_data.get("years_of_experience"):
            parts.append(f"経験年数: {resume_data['years_of_experience']}")
        
        if resume_data.get("summary"):
            parts.append(f"\n職務要約:\n{resume_data['summary']}")
        
        if resume_data.get("programming_languages"):
            parts.append(f"\nプログラミング言語: {', '.join(resume_data['programming_languages'])}")
        
        if resume_data.get("frameworks"):
            parts.append(f"フレームワーク: {', '.join(resume_data['frameworks'])}")
        
        if resume_data.get("work_experiences"):
            parts.append("\n職務経歴:")
            for exp in resume_data["work_experiences"]:
                parts.append(f"【{exp.get('company_name')} - {exp.get('position')}】")
                parts.append(f"期間: {exp.get('period')}")
                if exp.get("description"):
                    parts.append(f"職務内容: {exp['description']}")
        
        if resume_data.get("personal_projects"):
            parts.append("\n個人開発:")
            for proj in resume_data["personal_projects"]:
                parts.append(f"【{proj.get('title')}】")
                if proj.get("description"):
                    parts.append(f"説明: {proj['description']}")
                if proj.get("technologies"):
                    parts.append(f"技術: {', '.join(proj['technologies'])}")
        
        return "\n".join(parts)
