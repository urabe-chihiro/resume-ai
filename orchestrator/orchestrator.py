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

# オーケストレーター = 指揮者
# 5つの独立したエージェントを「指揮」して、順番に実行させ、結果を連結させて最終成果物を生成するクラス
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
        
        # 1. 企業分析
        company_info_text = self._format_company_info(job_requirements.company_info)
        company_analysis_output = self.company_analysis_agent.run({
            "company_info": company_info_text,
            "job_description": job_requirements.job_description,
        })
        results["company_analysis"] = company_analysis_output["analysis"]
        
        # 2. 求人要件抽出
        requirements_output = self.requirements_agent.run({
            "job_description": job_requirements.job_description,
            "company_analysis": results["company_analysis"],
        })
        results["requirements_analysis"] = requirements_output["requirements"]
        
        # 3. 職務経歴書構成計画
        user_input_text = self._format_user_input(user_input)
        structure_output = self.structure_agent.run({
            "user_experience": user_input_text,
            "job_requirements": requirements_output["requirements"],
            "company_analysis": results["company_analysis"],
        })
        results["structure_plan"] = structure_output["structure_plan"]
        
        # 4. 職務経歴書生成
        generation_output = self.generation_agent.run({
            "user_input": user_input_text,
            "job_requirements": job_requirements.job_description,
            "company_analysis": results["company_analysis"],
            "requirements_analysis": results["requirements_analysis"],
            "structure_plan": results["structure_plan"],
        })
        results["resume_markdown"] = generation_output["resume_markdown"]
        
        # 5. PDF生成用の構造化データ抽出
        results["resume_data"] = self._extract_structured_data(user_input, job_requirements)
        
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
    
    def generate_summary(
        self,
        user_input: UserInput,
        job_requirements: JobRequirements,
        company_analysis: str,
        requirements_analysis: str,
    ) -> str:
        """Generate a professional summary for the resume.
        
        Args:
            user_input: User's profile and experience
            job_requirements: Job requirements and company info
            company_analysis: Company analysis result
            requirements_analysis: Requirements analysis result
            
        Returns:
            Generated summary text
        """
        from prompts import SUMMARY_GENERATION_PROMPT
        from langchain_openai import ChatOpenAI
        
        # Format the input data
        programming_languages = ", ".join(user_input.programming_languages) if user_input.programming_languages else "記載なし"
        frameworks = ", ".join(user_input.frameworks) if user_input.frameworks else "記載なし"
        testing_tools = ", ".join(user_input.testing_tools) if user_input.testing_tools else "記載なし"
        design_tools = ", ".join(user_input.design_tools) if user_input.design_tools else "記載なし"
        
        personal_projects = ""
        if user_input.personal_projects:
            for proj in user_input.personal_projects:
                personal_projects += f"\n【{proj.title}】\n{proj.description}\n"
                if proj.technologies:
                    personal_projects += f"使用技術: {', '.join(proj.technologies)}\n"
        else:
            personal_projects = "記載なし"
        
        user_info = self._format_user_input(user_input)
        
        # Format the prompt
        prompt = SUMMARY_GENERATION_PROMPT.format(
            appeal_points=user_input.job_title or "スキルシートを参照",
            programming_languages=programming_languages,
            frameworks=frameworks,
            testing_tools=testing_tools,
            design_tools=design_tools,
            personal_projects=personal_projects,
            work_experiences=user_info,
            requirements_analysis=requirements_analysis,
            company_analysis=company_analysis,
        )
        
        # Generate summary using LLM
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        response = llm.invoke(prompt)
        
        return response.content
    
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
    
    def _format_user_input(self, user_input: UserInput) -> str:
        """Format complete user input for agents."""
    def _format_user_input(self, user_input: UserInput) -> str:
        """Format complete user input for agents."""
        parts = [
            f"氏名: {user_input.name}",
        ]
        
        if user_input.residence:
            parts.append(f"在住地: {user_input.residence}")
        
        if user_input.job_title:
            parts.append(f"職種: {user_input.job_title}")
        
        if user_input.years_of_experience:
            parts.append(f"経験年数: {user_input.years_of_experience}")
        
        if user_input.programming_languages:
            parts.append(f"\nプログラミング言語: {', '.join(user_input.programming_languages)}")
        
        if user_input.frameworks:
            parts.append(f"フレームワーク: {', '.join(user_input.frameworks)}")
        
        if user_input.testing_tools:
            parts.append(f"テストツール: {', '.join(user_input.testing_tools)}")
        
        if user_input.design_tools:
            parts.append(f"デザインツール: {', '.join(user_input.design_tools)}")
        
        if user_input.personal_projects:
            parts.append("\n個人開発:")
            for proj in user_input.personal_projects:
                parts.append(f"【{proj.title}】")
                parts.append(proj.description)
                if proj.technologies:
                    parts.append(f"使用技術: {', '.join(proj.technologies)}")
        
        if user_input.portfolio_url:
            parts.append(f"\nポートフォリオ: {user_input.portfolio_url}")
        
        return "\n".join(parts)
    
    def _extract_structured_data(self, user_input: UserInput, job_requirements: JobRequirements) -> Dict[str, Any]:
        """Extract structured data from UserInput for PDF generation.
        
        Args:
            user_input: User's profile and experience
            job_requirements: Job requirements and company info
            
        Returns:
            Dictionary with structured resume data for data_to_pdf()
        """
        # Build structured data
        structured_data = {
            "name": user_input.name,
            "residence": user_input.residence or "",
            "job_title": user_input.job_title or "",
            "years_of_experience": user_input.years_of_experience or "",
            "programming_languages": user_input.programming_languages,
            "frameworks": user_input.frameworks,
            "testing_tools": user_input.testing_tools,
            "design_tools": user_input.design_tools,
            "personal_projects": [
                {
                    "title": proj.title,
                    "description": proj.description,
                    "technologies": proj.technologies,
                    "url": proj.url,
                    "date": proj.date,
                }
                for proj in user_input.personal_projects
            ],
            "portfolio_url": user_input.portfolio_url or "",
        }
        
        return structured_data

