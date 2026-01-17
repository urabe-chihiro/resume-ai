"""Feedback improvement prompt template."""

FEEDBACK_IMPROVEMENT_PROMPT = """あなたは職務経歴書の改善専門家です。以下の職務経歴書に対するフィードバックを基に、改善版を作成してください。

現在の職務経歴書:
{current_resume}

フィードバック:
{feedback}

元の情報:
- 応募者情報: {user_input}
- 求人情報: {job_requirements}

以下の観点から改善してください:
1. フィードバックで指摘された問題点の修正
2. より効果的な表現への変更
3. 不足している情報の追加
4. 冗長な部分の削減
5. 全体の一貫性とバランスの向上

改善版をMarkdown形式で出力してください。
主要な変更点も簡単に説明してください。
"""
