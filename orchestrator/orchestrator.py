"""Agent orchestrator for coordinating workflow."""

from typing import Dict, Any, Optional
from agents import (
    CompanyAnalysisAgent,
    RequirementsExtractionAgent,
    ResumeStructureAgent,
    ResumeGenerationAgent,
    FeedbackImprovementAgent,
)
from models import UserInput, JobRequirements


class AgentOrchestrator:
    """Orchestrates the agent workflow for resume generation."""
    
    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.company_analysis_agent = CompanyAnalysisAgent()
        self.requirements_agent = RequirementsExtractionAgent()
        self.structure_agent = ResumeStructureAgent()
        self.generation_agent = ResumeGenerationAgent()
        self.improvement_agent = FeedbackImprovementAgent()
    
    def generate_resume(
        self,
        user_input: UserInput,
        job_requirements: JobRequirements,
    ) -> Dict[str, Any]:
        """Generate resume through the complete agent pipeline.
        
        Args:
            user_input: User's profile and experience
            job_requirements: Job requirements and company info
            
        Returns:
            Dictionary containing the generated resume and intermediate results
        """
        results = {}
        
        # Step 1: Company Analysis
        company_info_text = self._format_company_info(job_requirements.company_info)
        company_analysis_output = self.company_analysis_agent.run({
            "company_info": company_info_text,
            "job_description": job_requirements.job_description,
        })
        results["company_analysis"] = company_analysis_output["analysis"]
        
        # Step 2: Requirements Extraction
        requirements_output = self.requirements_agent.run({
            "job_description": job_requirements.job_description,
            "company_analysis": results["company_analysis"],
        })
        results["requirements_analysis"] = requirements_output["requirements"]
        
        # Step 3: Resume Structure Planning
        user_experience_text = self._format_user_experience(user_input)
        structure_output = self.structure_agent.run({
            "user_experience": user_experience_text,
            "job_requirements": requirements_output["requirements"],
            "company_analysis": results["company_analysis"],
        })
        results["structure_plan"] = structure_output["structure_plan"]
        
        # Step 4: Resume Generation
        user_input_text = self._format_user_input(user_input)
        generation_output = self.generation_agent.run({
            "user_input": user_input_text,
            "job_requirements": job_requirements.job_description,
            "company_analysis": results["company_analysis"],
            "requirements_analysis": results["requirements_analysis"],
            "structure_plan": results["structure_plan"],
        })
        results["resume_markdown"] = generation_output["resume_markdown"]
        
        return results
    
    def improve_resume(
        self,
        current_resume: str,
        feedback: str,
        user_input: UserInput,
        job_requirements: JobRequirements,
    ) -> str:
        """Improve resume based on feedback.
        
        Args:
            current_resume: Current resume markdown
            feedback: Feedback for improvement
            user_input: User's profile and experience
            job_requirements: Job requirements and company info
            
        Returns:
            Improved resume markdown
        """
        user_input_text = self._format_user_input(user_input)
        
        improvement_output = self.improvement_agent.run({
            "current_resume": current_resume,
            "feedback": feedback,
            "user_input": user_input_text,
            "job_requirements": job_requirements.job_description,
        })
        
        return improvement_output["improved_resume"]
    
    def _format_company_info(self, company_info) -> str:
        """Format company info for agents."""
        parts = [
            f"企業名: {company_info.name}",
        ]
        if company_info.industry:
            parts.append(f"業界: {company_info.industry}")
        if company_info.size:
            parts.append(f"規模: {company_info.size}")
        if company_info.culture:
            parts.append(f"企業文化: {company_info.culture}")
        if company_info.values:
            parts.append(f"企業価値観: {', '.join(company_info.values)}")
        
        return "\n".join(parts)
    
    def _format_user_experience(self, user_input: UserInput) -> str:
        """Format user experience for agents."""
        parts = []
        
        for exp in user_input.work_experiences:
            exp_text = f"【{exp.company} - {exp.position}】\n"
            exp_text += f"期間: {exp.start_date} 〜 {exp.end_date or '現在'}\n"
            exp_text += f"内容: {exp.description}\n"
            if exp.technologies:
                exp_text += f"技術: {', '.join(exp.technologies)}\n"
            parts.append(exp_text)
        
        return "\n\n".join(parts)
    
    def _format_user_input(self, user_input: UserInput) -> str:
        """Format complete user input for agents."""
        parts = [
            f"氏名: {user_input.name}",
            f"メール: {user_input.email}",
        ]
        
        if user_input.phone:
            parts.append(f"電話: {user_input.phone}")
        
        if user_input.summary:
            parts.append(f"\n職務要約:\n{user_input.summary}")
        
        if user_input.work_experiences:
            parts.append("\n職務経歴:")
            for exp in user_input.work_experiences:
                exp_text = f"\n【{exp.company} - {exp.position}】"
                exp_text += f"\n期間: {exp.start_date} 〜 {exp.end_date or '現在'}"
                exp_text += f"\n{exp.description}"
                if exp.technologies:
                    exp_text += f"\n使用技術: {', '.join(exp.technologies)}"
                parts.append(exp_text)
        
        if user_input.education:
            parts.append("\n学歴:")
            for edu in user_input.education:
                parts.append(f"- {edu.institution} {edu.degree} ({edu.field}) - {edu.graduation_date}")
        
        if user_input.skills:
            parts.append("\nスキル:")
            for skill in user_input.skills:
                parts.append(f"- {skill.category}: {', '.join(skill.items)}")
        
        if user_input.certifications:
            parts.append(f"\n資格: {', '.join(user_input.certifications)}")
        
        if user_input.languages:
            parts.append(f"\n言語: {', '.join(user_input.languages)}")
        
        return "\n".join(parts)
