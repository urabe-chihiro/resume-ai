"""Supplement integration agent for incorporating additional information into resume."""

import json
from typing import Dict, Any
from .base_agent import BaseAgent
from prompts import SUPPLEMENT_INTEGRATION_PROMPT


class SupplementIntegrationAgent(BaseAgent):
    """Agent for integrating supplementary information into the resume."""
    
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate supplementary information into resume data.
        
        Args:
            input_data: Must contain 'resume_data' and 'supplement_info'
            
        Returns:
            Updated resume data dictionary
        """
        resume_data = input_data.get("resume_data", {})
        supplement_info = input_data.get("supplement_info", "")
        
        if not supplement_info.strip():
            return resume_data
        
        # Format resume data for prompt
        resume_data_text = self._format_resume_data(resume_data)
        
        print("[SupplementIntegration] Integrating supplementary information into resume...")
        
        prompt = self._format_prompt(
            SUPPLEMENT_INTEGRATION_PROMPT,
            resume_data=resume_data_text,
            supplement_info=supplement_info,
        )
        
        print("[SupplementIntegration] Calling LLM...")
        response = self.llm.invoke(prompt)
        
        # Extract content from response
        if hasattr(response, 'content'):
            response_text = response.content
        else:
            response_text = str(response)
        
        print(f"[SupplementIntegration] LLM Response received ({len(response_text)} chars)")
        
        # Parse JSON response
        try:
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                updated_data = json.loads(json_str)
                print("[SupplementIntegration] Successfully integrated supplementary information")
                return updated_data
            else:
                print("[SupplementIntegration] No JSON found in response, returning original data")
                return resume_data
                
        except (json.JSONDecodeError, ValueError) as e:
            print(f"[SupplementIntegration] JSON parse error: {type(e).__name__}: {e}")
            print(f"[SupplementIntegration] Returning original data")
            import traceback
            traceback.print_exc()
            return resume_data
    
    def _format_resume_data(self, resume_data: Dict[str, Any]) -> str:
        """Format resume data for the prompt."""
        parts = []
        
        if resume_data.get("name"):
            parts.append(f"氏名: {resume_data['name']}")
        
        if resume_data.get("job_title"):
            parts.append(f"職種: {resume_data['job_title']}")
        
        if resume_data.get("residence"):
            parts.append(f"在中: {resume_data['residence']}")
        
        if resume_data.get("years_of_experience"):
            parts.append(f"経験年数: {resume_data['years_of_experience']}")
        
        if resume_data.get("summary"):
            parts.append(f"\n職務要約:\n{resume_data['summary']}")
        
        if resume_data.get("programming_languages"):
            parts.append(f"\nプログラミング言語: {', '.join(resume_data['programming_languages'])}")
        
        if resume_data.get("frameworks"):
            parts.append(f"フレームワーク: {', '.join(resume_data['frameworks'])}")
        
        if resume_data.get("testing_tools"):
            parts.append(f"テストツール: {', '.join(resume_data['testing_tools'])}")
        
        if resume_data.get("design_tools"):
            parts.append(f"デザインツール: {', '.join(resume_data['design_tools'])}")
        
        if resume_data.get("work_experiences"):
            parts.append("\n職務経歴:")
            for exp in resume_data["work_experiences"]:
                parts.append(f"\n【{exp.get('company_name')} - {exp.get('position')}】")
                parts.append(f"期間: {exp.get('period')}")
                if exp.get("description"):
                    parts.append(f"職務内容: {exp['description']}")
                if exp.get("technologies"):
                    parts.append(f"使用技術: {', '.join(exp['technologies'])}")
                if exp.get("achievements"):
                    parts.append(f"実績: {', '.join(exp['achievements'])}")
        
        if resume_data.get("personal_projects"):
            parts.append("\n個人開発:")
            for proj in resume_data["personal_projects"]:
                parts.append(f"\n【{proj.get('title')}】")
                if proj.get("description"):
                    parts.append(f"説明: {proj['description']}")
                if proj.get("technologies"):
                    parts.append(f"技術: {', '.join(proj['technologies'])}")
                if proj.get("url"):
                    parts.append(f"URL: {proj['url']}")
        
        if resume_data.get("portfolio_url"):
            parts.append(f"\nポートフォリオURL: {resume_data['portfolio_url']}")
        
        return "\n".join(parts)
