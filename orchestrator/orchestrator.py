"""Agent orchestrator for coordinating workflow."""

from typing import Dict, Any, Optional
from agents import (
    CompanyAnalysisAgent,
    RequirementsExtractionAgent,
    ResumeStructureAgent,
    ResumeGenerationAgent,
    FeedbackImprovementAgent,
    SummaryGenerationAgent,
    WorkExperienceRefinementAgent,
)
from models import UserInput, JobRequirements

# オーケストレーター = 指揮者
# 複数の独立したエージェントを「指揮」して、順番に実行させ、結果を連結させて最終成果物を生成するクラス
class AgentOrchestrator:
    """Orchestrates the agent workflow for resume generation."""
    
    def __init__(self):
        """Initialize orchestrator with all agents."""
        self.company_analysis_agent = CompanyAnalysisAgent()
        self.requirements_agent = RequirementsExtractionAgent()
        self.structure_agent = ResumeStructureAgent()
        self.generation_agent = ResumeGenerationAgent()
        self.improvement_agent = FeedbackImprovementAgent()
        self.summary_agent = SummaryGenerationAgent()
        self.work_experience_refinement_agent = WorkExperienceRefinementAgent()
    
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
        
        # 3. 職務経歴の校閲（求人に合わせて職務内容を修正）
        refined_experiences = []
        try:
            if user_input.work_experiences:
                print(f"[Orchestrator] Step 3: Refining {len(user_input.work_experiences)} work experiences")
                work_experiences_text = self._format_work_experiences(user_input)
                work_experience_refinement_output = self.work_experience_refinement_agent.run({
                    "work_experiences": work_experiences_text,
                    "job_title": job_requirements.job_title,
                    "job_requirements": job_requirements.job_description,
                    "requirements_analysis": results["requirements_analysis"],
                    "company_analysis": results["company_analysis"],
                })
                refined_experiences = work_experience_refinement_output.get("refined_experiences", [])
                print(f"[Orchestrator] Agent returned: {len(refined_experiences)} refined experiences")
                
                # Log details about what we got back
                if refined_experiences:
                    print(f"[Orchestrator] First refined experience keys: {refined_experiences[0].keys() if isinstance(refined_experiences[0], dict) else 'Not a dict'}")
                    if isinstance(refined_experiences[0], dict) and "description" in refined_experiences[0]:
                        print(f"[Orchestrator] First refined description (first 100 chars): {refined_experiences[0]['description'][:100]}")
                else:
                    print("[Orchestrator] No refined experiences - will use original")
                
                print(f"[Orchestrator] Refinement complete: {len(refined_experiences)} refined experiences returned")
            else:
                print("[Orchestrator] Step 3: No work experiences to refine")
        except Exception as e:
            # If refinement fails, just use empty list (original will be used in _extract_structured_data)
            print(f"[Orchestrator] Warning: Work experience refinement failed: {e}")
            import traceback
            traceback.print_exc()
            refined_experiences = []
        
        results["refined_work_experiences"] = refined_experiences
        
        # 4. 職務経歴書構成計画
        user_input_text = self._format_user_input(user_input)
        structure_output = self.structure_agent.run({
            "user_experience": user_input_text,
            "job_requirements": requirements_output["requirements"],
            "company_analysis": results["company_analysis"],
        })
        results["structure_plan"] = structure_output["structure_plan"]
        
        # 5. PDF生成用の構造化データ抽出（校閲済みの職務経歴を使用）
        results["resume_data"] = self._extract_structured_data(user_input, job_requirements, refined_experiences)
        
        return results
    
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
        # Format the input data
        programming_languages = ", ".join(user_input.programming_languages) if user_input.programming_languages else "記載なし"
        frameworks = ", ".join(user_input.frameworks) if user_input.frameworks else "記載なし"
        testing_tools = ", ".join(user_input.testing_tools) if user_input.testing_tools else "記載なし"
        design_tools = ", ".join(user_input.design_tools) if user_input.design_tools else "記載なし"
        
        work_experiences = ""
        if user_input.work_experiences:
            for exp in user_input.work_experiences:
                work_experiences += f"\n【{exp.company_name} - {exp.position}】\n"
                work_experiences += f"期間: {exp.period}\n"
                if exp.description:
                    work_experiences += f"{exp.description}\n"
        else:
            work_experiences = "記載なし"
        
        personal_projects = ""
        if user_input.personal_projects:
            for proj in user_input.personal_projects:
                personal_projects += f"\n【{proj.title}】\n{proj.description}\n"
                if proj.technologies:
                    personal_projects += f"使用技術: {', '.join(proj.technologies)}\n"
        else:
            personal_projects = "記載なし"
        
        # Use SummaryGenerationAgent to generate summary
        summary_output = self.summary_agent.run({
            "appeal_points": user_input.appeal_points or "スキルシートを参照",
            "work_experiences": work_experiences,
            "programming_languages": programming_languages,
            "frameworks": frameworks,
            "testing_tools": testing_tools,
            "design_tools": design_tools,
            "personal_projects": personal_projects,
            "company_analysis": company_analysis,
            "requirements_analysis": requirements_analysis,
        })
        
        return summary_output["summary"]
    
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
    
    def _format_work_experiences(self, user_input: UserInput) -> str:
        """Format work experiences for refinement agent.
        
        Args:
            user_input: User's profile and experience
            
        Returns:
            Formatted work experiences string
        """
        if not user_input.work_experiences:
            return "記載なし"
        
        parts = []
        for exp in user_input.work_experiences:
            parts.append(f"企業名: {exp.company_name}")
            parts.append(f"職位: {exp.position}")
            parts.append(f"期間: {exp.period}")
            if exp.description:
                parts.append(f"職務内容・成果:\n{exp.description}")
            parts.append("")
        
        return "\n".join(parts)
    
    def _extract_structured_data(self, user_input: UserInput, job_requirements: JobRequirements, refined_experiences: list = None) -> Dict[str, Any]:
        """Extract structured data from UserInput for PDF generation.
        
        Args:
            user_input: User's profile and experience
            job_requirements: Job requirements and company info
            refined_experiences: Refined work experiences from refinement agent
            
        Returns:
            Dictionary with structured resume data for data_to_pdf()
        """
        # Use refined experiences if available, otherwise use original
        if refined_experiences:
            work_exp_list = refined_experiences
        else:
            work_exp_list = [
                {
                    "company_name": exp.company_name,
                    "position": exp.position,
                    "period": exp.period,
                    "description": exp.description,
                }
                for exp in user_input.work_experiences
            ]
        
        # Build structured data
        structured_data = {
            "name": user_input.name,
            "residence": user_input.residence or "",
            "job_title": user_input.job_title or "",
            "role": job_requirements.job_title or "",  # Role is the target job title
            "years_of_experience": user_input.years_of_experience or "",
            "email": "",  # Email not stored in UserInput
            "phone": "",  # Phone not stored in UserInput
            "programming_languages": user_input.programming_languages,
            "frameworks": user_input.frameworks,
            "testing_tools": user_input.testing_tools,
            "design_tools": user_input.design_tools,
            "work_experiences": work_exp_list,
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

