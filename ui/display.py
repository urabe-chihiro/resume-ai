"""Display components for results."""

import streamlit as st
from typing import Dict, Any


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
        st.markdown(resume_markdown)
        
        st.markdown("---")
        st.markdown("### ダウンロード")
        
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📥 Markdownをダウンロード",
                data=resume_markdown,
                file_name="resume.md",
                mime="text/markdown",
            )
    
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
