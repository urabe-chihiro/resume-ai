"""Input form components for Streamlit."""

import streamlit as st
from typing import Dict, Any
from models import UserInput, WorkExperience, Education, Skill, JobRequirements, CompanyInfo


def render_input_form() -> Dict[str, Any]:
    """Render the complete input form.
    
    Returns:
        Dictionary containing user input and job requirements
    """
    st.title("AI職務経歴書生成システム")
    st.markdown("---")
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["📝 個人情報・経歴", "💼 求人情報"])
    
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
    st.header("個人情報")
    
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("氏名 *", key="name")
        email = st.text_input("メールアドレス *", key="email")
    with col2:
        phone = st.text_input("電話番号", key="phone")
    
    st.markdown("---")
    st.header("職務要約")
    summary = st.text_area(
        "あなたの職務経歴を簡潔に要約してください",
        height=100,
        key="summary",
        help="3-5行程度で、あなたの経験と強みを記述してください"
    )
    
    st.markdown("---")
    st.header("職務経歴")
    
    # Work experiences
    num_experiences = st.number_input("職務経歴の数", min_value=0, max_value=10, value=1, key="num_exp")
    work_experiences = []
    
    for i in range(int(num_experiences)):
        with st.expander(f"職務経歴 {i+1}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            with col1:
                company = st.text_input("会社名", key=f"exp_company_{i}")
                position = st.text_input("役職", key=f"exp_position_{i}")
            with col2:
                start_date = st.text_input("開始日 (例: 2020年4月)", key=f"exp_start_{i}")
                end_date = st.text_input("終了日 (現在の場合は空欄)", key=f"exp_end_{i}")
            
            description = st.text_area("職務内容・実績", height=100, key=f"exp_desc_{i}")
            technologies = st.text_input("使用技術 (カンマ区切り)", key=f"exp_tech_{i}")
            
            if company and position:
                work_experiences.append({
                    "company": company,
                    "position": position,
                    "start_date": start_date,
                    "end_date": end_date if end_date else None,
                    "description": description,
                    "technologies": [t.strip() for t in technologies.split(",")] if technologies else [],
                })
    
    st.markdown("---")
    st.header("学歴")
    
    num_education = st.number_input("学歴の数", min_value=0, max_value=5, value=1, key="num_edu")
    education = []
    
    for i in range(int(num_education)):
        with st.expander(f"学歴 {i+1}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            with col1:
                institution = st.text_input("学校名", key=f"edu_inst_{i}")
                degree = st.text_input("学位", key=f"edu_degree_{i}")
            with col2:
                field = st.text_input("専攻", key=f"edu_field_{i}")
                graduation_date = st.text_input("卒業年月", key=f"edu_grad_{i}")
            
            gpa = st.text_input("GPA (任意)", key=f"edu_gpa_{i}")
            
            if institution and degree:
                education.append({
                    "institution": institution,
                    "degree": degree,
                    "field": field,
                    "graduation_date": graduation_date,
                    "gpa": gpa if gpa else None,
                })
    
    st.markdown("---")
    st.header("スキル")
    
    num_skills = st.number_input("スキルカテゴリの数", min_value=0, max_value=10, value=2, key="num_skills")
    skills = []
    
    for i in range(int(num_skills)):
        col1, col2 = st.columns([1, 3])
        with col1:
            category = st.text_input("カテゴリ", key=f"skill_cat_{i}", 
                                    placeholder="例: プログラミング言語")
        with col2:
            items = st.text_input("スキル (カンマ区切り)", key=f"skill_items_{i}",
                                 placeholder="例: Python, Java, JavaScript")
        
        if category and items:
            skills.append({
                "category": category,
                "items": [item.strip() for item in items.split(",")],
            })
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("資格")
        certifications_text = st.text_area("資格 (1行に1つ)", key="certifications", height=100)
        certifications = [c.strip() for c in certifications_text.split("\n") if c.strip()]
    
    with col2:
        st.subheader("言語")
        languages_text = st.text_area("言語 (1行に1つ)", key="languages", height=100)
        languages = [l.strip() for l in languages_text.split("\n") if l.strip()]
    
    return {
        "name": name,
        "email": email,
        "phone": phone,
        "summary": summary,
        "work_experiences": work_experiences,
        "education": education,
        "skills": skills,
        "certifications": certifications,
        "languages": languages,
    }


def _render_job_requirements_form() -> Dict[str, Any]:
    """Render job requirements form."""
    st.header("企業情報")
    
    col1, col2 = st.columns(2)
    with col1:
        company_name = st.text_input("企業名 *", key="company_name")
        industry = st.text_input("業界", key="industry")
    with col2:
        company_size = st.text_input("企業規模", key="company_size", 
                                     placeholder="例: 100-500名")
    
    culture = st.text_area("企業文化", height=80, key="culture")
    values_text = st.text_input("企業価値観 (カンマ区切り)", key="values")
    values = [v.strip() for v in values_text.split(",")] if values_text else []
    
    st.markdown("---")
    st.header("求人情報")
    
    job_title = st.text_input("職種 *", key="job_title")
    job_description = st.text_area("職務内容 *", height=200, key="job_description",
                                   help="求人票の内容をそのまま貼り付けてください")
    
    col1, col2 = st.columns(2)
    with col1:
        required_skills_text = st.text_area("必須スキル (1行に1つ)", height=100, key="required_skills")
        required_skills = [s.strip() for s in required_skills_text.split("\n") if s.strip()]
    
    with col2:
        preferred_skills_text = st.text_area("歓迎スキル (1行に1つ)", height=100, key="preferred_skills")
        preferred_skills = [s.strip() for s in preferred_skills_text.split("\n") if s.strip()]
    
    responsibilities_text = st.text_area("主な業務内容 (1行に1つ)", height=100, key="responsibilities")
    responsibilities = [r.strip() for r in responsibilities_text.split("\n") if r.strip()]
    
    qualifications_text = st.text_area("応募資格 (1行に1つ)", height=100, key="qualifications")
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
