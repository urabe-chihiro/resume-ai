"""Resume generation prompt template."""

RESUME_GENERATION_PROMPT = """あなたはプロフェッショナルな職務経歴書ライターです。以下の情報を基に、説得力のある職務経歴書を生成してください。

応募者情報:
{user_input}

求人情報:
{job_requirements}

企業分析:
{company_analysis}

要件分析:
{requirements_analysis}

構成案:
{structure_plan}

以下のガイドラインに従って職務経歴書を作成してください:
1. 応募職種に関連する経験・スキルを重点的にアピール
2. 具体的な数値・成果を含める
3. 企業が求める人物像に合致することを示す
4. 簡潔で読みやすい文章
5. プロフェッショナルな表現

Markdown形式で出力してください。
"""
