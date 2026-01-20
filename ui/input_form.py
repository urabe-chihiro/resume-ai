"""Input form components for Streamlit."""

import streamlit as st
from typing import Dict, Any
from models import UserInput, PersonalProject, JobRequirements, CompanyInfo
from db import FormDataManager


def render_input_form() -> Dict[str, Any]:
    """Render the complete input form.
    
    Returns:
        Dictionary containing user input and job requirements
    """
    st.title("AI職務経歴書生成システム")
    st.markdown("---")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📝 応募者情報", "💼 求人情報"])
    
    with tab1:
        user_data = _render_user_input_form()
    
    with tab2:
        job_data = _render_job_requirements_form()
    
    return {
        "user_input": user_data,
        "job_requirements": job_data,
    }


def _render_user_input_form() -> Dict[str, Any]:
    """Render user input form."""
    # Load previous data from database if available
    db_manager = FormDataManager()
    previous_data = db_manager.get_latest_user_input()
    
    st.header("基本情報")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input(
            "氏名 *", 
            key="name",
            value=previous_data.get("name", "") if previous_data else ""
        )
    with col2:
        residence = st.text_input(
            "在住地 (例: 神奈川県)", 
            key="residence",
            value=previous_data.get("residence", "") if previous_data else ""
        )
    
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input(
            "職種", 
            key="job_title",
            placeholder="例: バックエンドエンジニア",
            value=previous_data.get("job_title", "") if previous_data else ""
        )
    with col2:
        years_of_experience = st.text_input(
            "経験年数", 
            key="years_of_experience",
            placeholder="例: 15年間",
            value=previous_data.get("years_of_experience", "") if previous_data else ""
        )
    
    st.markdown("---")
    st.header("スキルセット")
    
    col1, col2 = st.columns(2)
    with col1:
        programming_langs = st.text_input(
            "プログラミング言語 (カンマ区切り)",
            key="programming_languages",
            placeholder="例: Python, Go, TypeScript",
            value=", ".join(previous_data.get("programming_languages", [])) if previous_data else ""
        )
        frameworks = st.text_input(
            "フレームワーク・ライブラリ (カンマ区切り)",
            key="frameworks",
            placeholder="例: React, FastAPI, LangChain",
            value=", ".join(previous_data.get("frameworks", [])) if previous_data else ""
        )
    with col2:
        testing_tools = st.text_input(
            "テストツール (カンマ区切り)",
            key="testing_tools",
            placeholder="例: Jest, pytest",
            value=", ".join(previous_data.get("testing_tools", [])) if previous_data else ""
        )
        design_tools = st.text_input(
            "デザインツール (カンマ区切り)",
            key="design_tools",
            placeholder="例: Figma, Sketch",
            value=", ".join(previous_data.get("design_tools", [])) if previous_data else ""
        )
    
    st.markdown("---")
    st.header("個人開発")
    
    default_num_projects = len(previous_data.get("personal_projects", [])) if previous_data else 0
    num_projects = st.number_input("個人開発プロジェクト数", min_value=0, max_value=5, value=default_num_projects, key="num_projects")
    personal_projects = []
    
    for i in range(int(num_projects)):
        prev_proj = previous_data.get("personal_projects", [])[i] if previous_data and i < len(previous_data.get("personal_projects", [])) else {}
        
        with st.expander(f"プロジェクト {i+1}", expanded=(i==0)):
            title = st.text_input("プロジェクト名", key=f"proj_title_{i}", value=prev_proj.get("title", ""))
            description = st.text_area("プロジェクト説明", height=80, key=f"proj_desc_{i}", value=prev_proj.get("description", ""))
            
            col1, col2 = st.columns(2)
            with col1:
                tech_list = ", ".join(prev_proj.get("technologies", [])) if prev_proj.get("technologies") else ""
                technologies = st.text_input("使用技術 (カンマ区切り)", key=f"proj_tech_{i}", value=tech_list)
            with col2:
                date = st.text_input("完成日・期間", key=f"proj_date_{i}", placeholder="例: 2024年1月", value=prev_proj.get("date", ""))
            
            url = st.text_input("プロジェクトURL", key=f"proj_url_{i}", value=prev_proj.get("url", "") if prev_proj.get("url") else "")
            
            if title and description:
                personal_projects.append({
                    "title": title,
                    "description": description,
                    "technologies": [t.strip() for t in technologies.split(",")] if technologies else [],
                    "date": date if date else None,
                    "url": url if url else None,
                })
    
    portfolio_url = st.text_input(
        "ポートフォリオ・GitHub URL",
        key="portfolio_url",
        placeholder="例: https://github.com/username",
        value=previous_data.get("portfolio_url", "") if previous_data else ""
    )
    
    return {
        "name": name,
        "residence": residence,
        "job_title": job_title,
        "years_of_experience": years_of_experience,
        "programming_languages": [lang.strip() for lang in programming_langs.split(",")] if programming_langs else [],
        "frameworks": [fw.strip() for fw in frameworks.split(",")] if frameworks else [],
        "testing_tools": [tool.strip() for tool in testing_tools.split(",")] if testing_tools else [],
        "design_tools": [tool.strip() for tool in design_tools.split(",")] if design_tools else [],
        "personal_projects": personal_projects,
        "portfolio_url": portfolio_url,
    }


def _render_job_requirements_form() -> Dict[str, Any]:
    """Render job requirements form."""
    # Load previous data from database if available
    db_manager = FormDataManager()
    previous_data = db_manager.get_latest_job_requirements()
    
    st.header("企業情報")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input(
            "企業名 *", 
            key="company_name",
            value=previous_data.get("company_info", {}).get("name", "") if previous_data else ""
        )
        industry = st.text_input(
            "業界", 
            key="industry",
            value=previous_data.get("company_info", {}).get("industry", "") if previous_data else ""
        )
    with col2:
        company_size = st.text_input(
            "企業規模", 
            key="company_size", 
            placeholder="例: 100-500名",
            value=previous_data.get("company_info", {}).get("size", "") if previous_data else ""
        )
    
    culture = st.text_area(
        "企業文化", 
        height=80, 
        key="culture",
        value=previous_data.get("company_info", {}).get("culture", "") if previous_data else ""
    )
    values_str = ", ".join(previous_data.get("company_info", {}).get("values", [])) if previous_data else ""
    values_text = st.text_input("企業価値観 (カンマ区切り)", key="values", value=values_str)
    values = [v.strip() for v in values_text.split(",")] if values_text else []
    
    st.markdown("---")
    st.header("求人情報")
    
    job_title = st.text_input(
        "職種 *", 
        key="job_title",
        value=previous_data.get("job_title", "") if previous_data else ""
    )
    job_description = st.text_area(
        "職務内容 *", 
        height=200, 
        key="job_description",
        value=previous_data.get("job_description", "") if previous_data else "",
                                   help="求人票の内容をそのまま貼り付けてください")
    
    col1, col2 = st.columns(2)
    with col1:
        req_skills_str = "\n".join(previous_data.get("required_skills", [])) if previous_data else ""
        required_skills_text = st.text_area("必須スキル (1行に1つ)", height=100, key="required_skills", value=req_skills_str)
        required_skills = [s.strip() for s in required_skills_text.split("\n") if s.strip()]
    
    with col2:
        pref_skills_str = "\n".join(previous_data.get("preferred_skills", [])) if previous_data else ""
        preferred_skills_text = st.text_area("歓迎スキル (1行に1つ)", height=100, key="preferred_skills", value=pref_skills_str)
        preferred_skills = [s.strip() for s in preferred_skills_text.split("\n") if s.strip()]
    
    resp_str = "\n".join(previous_data.get("responsibilities", [])) if previous_data else ""
    responsibilities_text = st.text_area("主な業務内容 (1行に1つ)", height=100, key="responsibilities", value=resp_str)
    responsibilities = [r.strip() for r in responsibilities_text.split("\n") if r.strip()]
    
    qual_str = "\n".join(previous_data.get("qualifications", [])) if previous_data else ""
    qualifications_text = st.text_area("応募資格 (1行に1つ)", height=100, key="qualifications", value=qual_str)
    qualifications = [q.strip() for q in qualifications_text.split("\n") if q.strip()]
    
    return {
        "job_title": job_title,
        "company_info": {
            "name": company_name,
            "industry": industry,
            "size": company_size,
            "culture": culture,
            "values": values,
        },
        "job_description": job_description,
        "required_skills": required_skills,
        "preferred_skills": preferred_skills,
        "responsibilities": responsibilities,
        "qualifications": qualifications,
    }
