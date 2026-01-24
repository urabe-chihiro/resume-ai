"""Display components for results."""

import streamlit as st
from typing import Dict, Any


def display_structured_preview(resume_data: Dict[str, Any]) -> None:
    """Display structured resume data as formatted preview.
    
    Args:
        resume_data: Structured resume data dictionary
    """
    # 1. 個人情報セクション
    st.markdown("## 個人情報")
    
    header_info = []
    if resume_data.get("name"):
        header_info.append(f"**{resume_data['name']}**")
    if resume_data.get("job_title"):
        header_info.append(f"**{resume_data['job_title']}**")
    if header_info:
        st.markdown(" | ".join(header_info))
    
    contact_info = []
    if resume_data.get("residence"):
        contact_info.append(f"📍 {resume_data['residence']}")
    if resume_data.get("years_of_experience"):
        contact_info.append(f"📅 {resume_data['years_of_experience']}")
    if contact_info:
        st.markdown(" | ".join(contact_info))
    
    st.markdown("---")
    
    # 2. アピールポイント - LLMで生成されたもの（タイトルなし）
    if resume_data.get("summary"):
        # Display summary with preserved line breaks for proper paragraph formatting
        st.write(resume_data["summary"])
        st.markdown("")
    
    st.markdown("---")
    
    # 3. スキルセット
    st.markdown("## スキルセット")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if resume_data.get("programming_languages"):
            langs = "、".join(resume_data["programming_languages"])
            st.markdown(f"**プログラミング言語:** {langs}")
        
        if resume_data.get("frameworks"):
            fws = "、".join(resume_data["frameworks"])
            st.markdown(f"**フレームワーク:** {fws}")
    
    with col2:
        if resume_data.get("testing_tools"):
            tools = "、".join(resume_data["testing_tools"])
            st.markdown(f"**テストツール:** {tools}")
        
        if resume_data.get("design_tools"):
            design = "、".join(resume_data["design_tools"])
            st.markdown(f"**デザインツール:** {design}")
    
    st.markdown("")
    
    # 4. 個人開発の成果物
    if resume_data.get("personal_projects") and len(resume_data["personal_projects"]) > 0:
        st.markdown("---")
        st.markdown("## 個人開発")
        
        for project in resume_data["personal_projects"]:
            if project.get("title"):
                st.markdown(f"### {project['title']}")
                
                if project.get("date"):
                    st.markdown(f"**期間:** {project['date']}")
                
                if project.get("description"):
                    st.markdown(project["description"])
                
                if project.get("technologies"):
                    tech_str = "、".join(project["technologies"])
                    st.markdown(f"**使用技術:** {tech_str}")
                
                if project.get("url"):
                    st.markdown(f"[プロジェクトリンク]({project['url']})")
                
                st.markdown("")
        
        if resume_data.get("portfolio_url"):
            st.markdown(f"**ポートフォリオ:** [{resume_data['portfolio_url']}]({resume_data['portfolio_url']})")
    
    # 5. 職務経歴
    if resume_data.get("work_experiences") and len(resume_data["work_experiences"]) > 0:
        st.markdown("---")
        st.markdown("## 職務経歴")
        
        for exp in resume_data["work_experiences"]:
            if exp.get("company_name"):
                st.markdown(f"### {exp['company_name']} - {exp.get('position', '')}")
                st.markdown(f"**期間:** {exp.get('period', '')}")
                
                if exp.get("description"):
                    st.markdown(exp["description"])
                
                st.markdown("")


def display_results(results: Dict[str, Any], resume_markdown: str) -> None:
    """Display generation results.
    
    Args:
        results: Dictionary containing intermediate results
        resume_markdown: Generated resume in markdown
    """
    st.success("✅ 職務経歴書の生成が完了しました！")
    
    # Display tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 生成された職務経歴書", "🔍 分析結果", "📊 処理詳細"])
    
    with tab1:
        st.markdown("### 職務経歴書プレビュー")
        
        # Display structured data preview if available
        if "resume_data" in results:
            display_structured_preview(results["resume_data"])
        else:
            # Fallback to markdown
            st.markdown(resume_markdown)
    
    with tab2:
        st.markdown("### 企業分析")
        with st.expander("企業分析結果を表示", expanded=True):
            st.markdown(results.get("company_analysis", ""))
        
        st.markdown("### 要件分析")
        with st.expander("要件分析結果を表示", expanded=True):
            st.markdown(results.get("requirements_analysis", ""))
        
        st.markdown("### 構成計画")
        with st.expander("構成計画を表示", expanded=True):
            st.markdown(results.get("structure_plan", ""))
    
    with tab3:
        st.markdown("### 処理ステップ")
        steps = [
            ("✅ 企業分析", "企業情報と求人内容の分析を完了しました"),
            ("✅ 要件抽出", "必須スキルと推奨スキルの抽出を完了しました"),
            ("✅ 構成計画", "最適な職務経歴書の構成を決定しました"),
            ("✅ 生成", "職務経歴書の生成を完了しました"),
        ]
        
        for step, description in steps:
            st.markdown(f"**{step}**")
            st.text(description)
            st.markdown("")


def display_improvement_form(current_resume: str) -> str:
    """Display form for improvement feedback.
    
    Args:
        current_resume: Current resume markdown
        
    Returns:
        Feedback text
    """
    st.markdown("---")
    st.header("📝 改善フィードバック")
    
    st.markdown("生成された職務経歴書について、改善したい点があればフィードバックをお願いします。")
    
    feedback = st.text_area(
        "改善点・追加したい内容",
        height=150,
        placeholder="例: もっと具体的な数値を入れたい、○○の経験を強調したい、など",
        key="feedback_text"
    )
    
    return feedback
