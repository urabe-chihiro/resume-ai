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
if "results" not in st.session_state:
    st.session_state.results = None
if "user_input_obj" not in st.session_state:
    st.session_state.user_input_obj = None
if "job_requirements_obj" not in st.session_state:
    st.session_state.job_requirements_obj = None
if "suggestions" not in st.session_state:
    st.session_state.suggestions = None
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""
if "updated_pdf_bytes" not in st.session_state:
    st.session_state.updated_pdf_bytes = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "do_upgrade_input" not in st.session_state:
    st.session_state.do_upgrade_input = None
if "do_regenerate_suggestions" not in st.session_state:
    st.session_state.do_regenerate_suggestions = False

# Initialize form data in session state
if "form_user_data" not in st.session_state:
    st.session_state.form_user_data = {}
if "form_job_data" not in st.session_state:
    st.session_state.form_job_data = {}


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
            generate_button = st.button("🚀 職務経歴書を生成", type="primary", use_container_width=True, disabled=st.session_state.processing)
        
        if generate_button:
            # Start processing - set flag and rerun to disable buttons
            if not st.session_state.processing:
                st.session_state.processing = True
                st.rerun()
        
        # Execute generation if processing flag is set
        if st.session_state.processing and not st.session_state.resume_generated:
            # Validate inputs
            user_valid, user_errors = validate_user_input(form_data["user_input"])
            job_valid, job_errors = validate_job_requirements(form_data["job_requirements"])
            
            if not user_valid:
                st.session_state.processing = False
                st.error("❌ 個人情報・経歴の入力に問題があります:")
                for error in user_errors:
                    st.error(f"• {error}")
                st.stop()
            
            if not job_valid:
                st.session_state.processing = False
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
                    appeal_points=form_data["user_input"].get("appeal_points"),
                    programming_languages=form_data["user_input"].get("programming_languages", []),
                    frameworks=form_data["user_input"].get("frameworks", []),
                    testing_tools=form_data["user_input"].get("testing_tools", []),
                    design_tools=form_data["user_input"].get("design_tools", []),
                    work_experiences=form_data["user_input"].get("work_experiences", []),
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
                    # Debug: Check if work_experiences is in form_data
                    if "work_experiences" in form_data["user_input"]:
                        print(f"DEBUG: work_experiences count: {len(form_data['user_input'].get('work_experiences', []))}")
                    else:
                        print("DEBUG: work_experiences NOT in form_data")
                    db_manager.save_user_input(form_data["user_input"])
                    db_manager.save_job_requirements(form_data["job_requirements"])
                except Exception as db_error:
                    # Database save is optional, don't fail if it errors
                    print(f"Warning: Could not save form data to database: {db_error}")
                    import traceback
                    traceback.print_exc()
                
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
                    
                    # Generate improvement suggestions
                    try:
                        suggestions_result = orchestrator.generate_improvement_suggestions(
                            results["resume_data"],
                            job_requirements,
                        )
                        st.session_state.suggestions = suggestions_result.get("suggestions", [])
                        st.session_state.prompt_text = suggestions_result.get("prompt_text", "")
                    except Exception as e:
                        print(f"Warning: Could not generate improvement suggestions: {e}")
                        st.session_state.suggestions = []
                        st.session_state.prompt_text = ""
                    
                    # Store in session state
                    st.session_state.results = results
                    st.session_state.resume_generated = True
                    st.session_state.processing = False
                    
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
                    st.session_state.processing = False
                    st.error(f"❌ 生成中にエラーが発生しました: {str(e)}")
                    st.exception(e)
    
    else:
        # Display results
        display_results(st.session_state.results, None)
        
        # Improvement suggestions section (moved before PDF output)
        st.markdown("---")
        
        # Use expander to make it clear this is an optional feature
        with st.expander("💡 補足情報の提案", expanded=True):
            st.info("📝 LLMが生成した提案を参考に、職務経歴書に追加情報を入力できます。")
            
            # Check if we should display suggestions
            has_suggestions = st.session_state.suggestions and len(st.session_state.suggestions) > 0
            
            # Display suggestions and input form
            if has_suggestions:
                st.markdown("#### 📌 提案内容")
                for i, suggestion in enumerate(st.session_state.suggestions, 1):
                    st.markdown(f"**{i}.** {suggestion}")
                
                st.markdown("---")
                
                # Input form for user to add supplementary information
                st.markdown("#### ✏️ 補足情報の入力")
                if st.session_state.prompt_text:
                    st.markdown(f"*{st.session_state.prompt_text}*")
            
            supplementary_input = st.text_area(
                "補足情報を入力してください",
                key="supplementary_info",
                height=150,
                placeholder="提案を参考に、職務経歴書に追加したい補足情報や経験を入力してください。複数の内容がある場合は改行で区切って入力してください。",
                help="ここに入力した情報は、職務要約の補足情報として職務経歴書に追加されます。"
            )
            
            # Button to apply and update resume
            col1, col2 = st.columns(2)
            with col1:
                if st.button("職務経歴書をアップグレード", type="primary", use_container_width=True, key="upgrade_resume", disabled=st.session_state.processing):
                    # Get input value and validate
                    input_value = st.session_state.get("supplementary_info", "").strip()
                    if input_value:
                        # Start processing
                        st.session_state.processing = True
                        st.session_state.do_upgrade_input = input_value
                        st.rerun()
                    else:
                        st.warning("⚠️ 補足情報を入力してください")
            
            # Execute upgrade if processing and input is available
            if st.session_state.processing and st.session_state.get("do_upgrade_input"):
                try:
                    with st.spinner("職務経歴書を更新中..."):
                        input_value = st.session_state.do_upgrade_input
                        # Use LLM to integrate supplementary information
                        orchestrator = AgentOrchestrator()
                        
                        # Integrate supplement info using LLM
                        updated_data = orchestrator.integrate_supplement_info(
                            st.session_state.results["resume_data"],
                            input_value
                        )
                        
                        # Update session state
                        st.session_state.results["resume_data"] = updated_data
                        
                        # Generate updated PDF automatically
                        import time
                        pdf_generator = SkillSheetGenerator()
                        output_path = f"/tmp/resume_updated_{int(time.time())}.pdf"
                        pdf_generator.data_to_pdf(updated_data, output_path)
                        
                        with open(output_path, "rb") as f:
                            st.session_state.updated_pdf_bytes = f.read()
                        
                        # Keep suggestions but clear the input
                        # Don't clear suggestions so user can see them after upgrade
                        
                        # Clear processing state
                        st.session_state.processing = False
                        st.session_state.do_upgrade_input = None
                        st.success("✅ 職務経歴書をアップグレードしました！")
                        st.rerun()
                except Exception as e:
                    st.session_state.processing = False
                    st.session_state.do_upgrade_input = None
                    st.error(f"❌ 更新エラー: {str(e)}")
                    import traceback
                    st.error(traceback.format_exc())
            
            with col2:
                if st.button("提案を再生成", use_container_width=True, key="regenerate_suggestions", disabled=st.session_state.processing):
                    # Start processing
                    st.session_state.processing = True
                    st.session_state.do_regenerate_suggestions = True
                    st.rerun()
            
            # Execute suggestion regeneration if flag is set
            if st.session_state.processing and st.session_state.get("do_regenerate_suggestions"):
                try:
                    with st.spinner("補足情報の提案を再生成中..."):
                        orchestrator = AgentOrchestrator()
                        suggestions_result = orchestrator.generate_improvement_suggestions(
                            st.session_state.results["resume_data"],
                            st.session_state.job_requirements_obj,
                        )
                        st.session_state.suggestions = suggestions_result.get("suggestions", [])
                        st.session_state.prompt_text = suggestions_result.get("prompt_text", "")
                        st.session_state.processing = False
                        st.session_state.do_regenerate_suggestions = False
                        st.rerun()
                except Exception as e:
                    st.session_state.processing = False
                    st.session_state.do_regenerate_suggestions = False
                    st.error(f"❌ 提案生成エラー: {str(e)}")
            else:
                # No suggestions generated yet
                st.info("補足情報の提案は職務経歴書の生成と同時に自動生成されます。")
        
        # PDF download (moved after suggestions section)
        st.markdown("---")
        st.markdown("### 📥 PDF出力")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            if st.session_state.updated_pdf_bytes:
                st.success("✅ アップグレード済みの最新PDFをダウンロードできます")
            else:
                st.info("PDFファイルとしてダウンロードできます")
        with col2:
            # Check if we have an updated PDF, if not, generate it
            if st.session_state.updated_pdf_bytes:
                # Use the updated PDF directly
                st.download_button(
                    label="📥 PDFをダウンロード",
                    data=st.session_state.updated_pdf_bytes,
                    file_name="resume.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True,
                )
            else:
                # Generate new PDF
                if st.button("PDF生成", type="secondary", use_container_width=True):
                    try:
                        with st.spinner("PDFを生成中..."):
                            import time
                            pdf_generator = SkillSheetGenerator()
                            # Use timestamp to avoid caching
                            output_path = f"/tmp/resume_{int(time.time())}.pdf"
                            
                            # Use structured data
                            pdf_generator.data_to_pdf(st.session_state.results["resume_data"], output_path)
                            
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
        
        # End of suggestions section placeholder
        # End of suggestions section placeholder


if __name__ == "__main__":
    main()
