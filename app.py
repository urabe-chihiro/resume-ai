"""Main application entry point for Resume AI."""

import os
import streamlit as st
import logging
from dotenv import load_dotenv

from models import UserInput, JobRequirements, CompanyInfo, PersonalProject
from orchestrator import AgentOrchestrator
from ui import render_input_form, validate_user_input, validate_job_requirements, display_results, display_improvement_form
from pdf.skill_sheet_generator import SkillSheetGenerator
from rag import VectorStore, DocumentManager
from db import FormDataManager

# Load environment variables
load_dotenv()

# Configure logging for OpenAI
logger = logging.getLogger("openai")
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# Configure Streamlit page
st.set_page_config(
    page_title="AI職務経歴書生成システム",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "resume_generated" not in st.session_state:
    st.session_state.resume_generated = False
if "current_resume" not in st.session_state:
    st.session_state.current_resume = None
if "results" not in st.session_state:
    st.session_state.results = None
if "user_input_obj" not in st.session_state:
    st.session_state.user_input_obj = None
if "job_requirements_obj" not in st.session_state:
    st.session_state.job_requirements_obj = None


def main():
    """Main application function."""
    
    # Sidebar
    with st.sidebar:
        st.title("📋 メニュー")
        st.markdown("---")
        
        st.markdown("### 使い方")
        st.markdown("""
        1. 個人情報・経歴を入力
        2. 応募する求人情報を入力
        3. 「職務経歴書を生成」をクリック
        4. 生成された職務経歴書を確認
        5. 必要に応じて改善フィードバックを入力
        """)
        
        st.markdown("---")
        st.markdown("### 設定")
        
        # Check for OpenAI API key
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.success("✅ OpenAI API キーが設定されています")
        else:
            st.error("❌ OpenAI API キーが設定されていません")
            st.markdown("`.env`ファイルに`OPENAI_API_KEY`を設定してください")
        
        st.markdown("---")
        if st.button("🔄 リセット", help="入力内容と生成結果をリセットします"):
            st.session_state.resume_generated = False
            st.session_state.current_resume = None
            st.session_state.results = None
            st.session_state.user_input_obj = None
            st.session_state.job_requirements_obj = None
            st.rerun()
    
    # Check API key before proceeding
    if not os.getenv("OPENAI_API_KEY"):
        st.error("⚠️ OpenAI API キーが設定されていません。サイドバーの設定を確認してください。")
        st.stop()
    
    # Main content
    if not st.session_state.resume_generated:
        # Input form
        form_data = render_input_form()
        
        st.markdown("---")
        
        # Generate button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            generate_button = st.button("🚀 職務経歴書を生成", type="primary", use_container_width=True)
        
        if generate_button:
            # Validate inputs
            user_valid, user_errors = validate_user_input(form_data["user_input"])
            job_valid, job_errors = validate_job_requirements(form_data["job_requirements"])
            
            if not user_valid:
                st.error("❌ 個人情報・経歴の入力に問題があります:")
                for error in user_errors:
                    st.error(f"• {error}")
                st.stop()
            
            if not job_valid:
                st.error("❌ 求人情報の入力に問題があります:")
                for error in job_errors:
                    st.error(f"• {error}")
                st.stop()
            
            # Convert to Pydantic models
            try:
                user_input = UserInput(
                    name=form_data["user_input"]["name"],
                    residence=form_data["user_input"].get("residence"),
                    job_title=form_data["user_input"].get("job_title"),
                    years_of_experience=form_data["user_input"].get("years_of_experience"),
                    programming_languages=form_data["user_input"].get("programming_languages", []),
                    frameworks=form_data["user_input"].get("frameworks", []),
                    testing_tools=form_data["user_input"].get("testing_tools", []),
                    design_tools=form_data["user_input"].get("design_tools", []),
                    personal_projects=form_data["user_input"].get("personal_projects", []),
                    portfolio_url=form_data["user_input"].get("portfolio_url"),
                )
                
                job_requirements = JobRequirements(
                    job_title=form_data["job_requirements"]["job_title"],
                    company_info=CompanyInfo(**form_data["job_requirements"]["company_info"]),
                    job_description=form_data["job_requirements"]["job_description"],
                    required_skills=form_data["job_requirements"].get("required_skills", []),
                    preferred_skills=form_data["job_requirements"].get("preferred_skills", []),
                    responsibilities=form_data["job_requirements"].get("responsibilities", []),
                    qualifications=form_data["job_requirements"].get("qualifications", []),
                )
                
                st.session_state.user_input_obj = user_input
                st.session_state.job_requirements_obj = job_requirements
                
                # Save form data to database
                try:
                    db_manager = FormDataManager()
                    db_manager.save_user_input(form_data["user_input"])
                    db_manager.save_job_requirements(form_data["job_requirements"])
                except Exception as db_error:
                    # Database save is optional, don't fail if it errors
                    print(f"Warning: Could not save form data to database: {db_error}")
                
            except Exception as e:
                st.error(f"❌ データ変換エラー: {str(e)}")
                st.stop()
            
            # Generate resume
            with st.spinner("職務経歴書を生成中... (1-2分程度かかります)"):
                try:
                    # Initialize orchestrator
                    orchestrator = AgentOrchestrator()
                    
                    # Generate resume
                    results = orchestrator.generate_resume(user_input, job_requirements)
                    
                    # Generate professional summary based on appeal points, skills, and personal projects
                    summary = orchestrator.generate_summary(
                        user_input,
                        job_requirements,
                        results["company_analysis"],
                        results["requirements_analysis"],
                    )
                    results["generated_summary"] = summary
                    
                    # Add summary to structured resume data
                    results["resume_data"]["summary"] = summary
                    
                    # Store in session state
                    st.session_state.results = results
                    st.session_state.current_resume = results["resume_markdown"]
                    st.session_state.resume_generated = True
                    
                    # Optional: Store in RAG for future reference
                    try:
                        vector_store = VectorStore()
                        doc_manager = DocumentManager(vector_store)
                        
                        # Store job application context
                        doc_manager.store_job_application_context(
                            job_id=f"{job_requirements.company_info.name}_{job_requirements.job_title}",
                            job_description=job_requirements.job_description,
                            company_name=job_requirements.company_info.name,
                            company_info=str(job_requirements.company_info),
                        )
                    except Exception as e:
                        # RAG storage is optional, don't fail if it errors
                        print(f"Warning: Could not store in RAG: {e}")
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 生成中にエラーが発生しました: {str(e)}")
                    st.exception(e)
    
    else:
        # Display results
        display_results(st.session_state.results, st.session_state.current_resume)
        
        # PDF download
        st.markdown("---")
        st.markdown("### 📥 PDF出力")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            st.info("PDFファイルとしてダウンロードすることもできます")
        with col2:
            if st.button("PDF生成", type="secondary", use_container_width=True):
                try:
                    with st.spinner("PDFを生成中..."):
                        import time
                        pdf_generator = SkillSheetGenerator()
                        # Use timestamp to avoid caching
                        output_path = f"/tmp/resume_{int(time.time())}.pdf"
                        
                        # Use structured data if available, otherwise fall back to markdown
                        if "resume_data" in st.session_state.results:
                            pdf_generator.data_to_pdf(st.session_state.results["resume_data"], output_path)
                        else:
                            pdf_generator.markdown_to_pdf(st.session_state.current_resume, output_path)
                        
                        with open(output_path, "rb") as f:
                            pdf_bytes = f.read()
                        
                        st.success("✅ PDF生成完了！")
                        st.download_button(
                            label="📥 PDFをダウンロード",
                            data=pdf_bytes,
                            file_name="resume.pdf",
                            mime="application/pdf",
                        )
                except Exception as e:
                    st.error(f"❌ PDF生成エラー: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
                    st.warning("💡 ヒント: 生成AI からのデータ形式が正しいか確認してください。")
        
        # Improvement form
        feedback = display_improvement_form(st.session_state.current_resume)
        
        if feedback and st.button("🔄 改善版を生成", type="primary"):
            with st.spinner("改善版を生成中..."):
                try:
                    orchestrator = AgentOrchestrator()
                    improved_resume = orchestrator.improve_resume(
                        current_resume=st.session_state.current_resume,
                        feedback=feedback,
                        user_input=st.session_state.user_input_obj,
                        job_requirements=st.session_state.job_requirements_obj,
                    )
                    
                    st.session_state.current_resume = improved_resume
                    st.success("✅ 改善版の生成が完了しました！")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ 改善版生成エラー: {str(e)}")


if __name__ == "__main__":
    main()
