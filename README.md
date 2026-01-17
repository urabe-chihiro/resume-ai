# Resume AI - AI職務経歴書生成システム

LangChainとStreamlitを使用したAI職務経歴書生成システムです。企業情報と求人要項を分析し、あなたの経歴に最適化された職務経歴書を自動生成します。

## 特徴

- 🤖 **AI駆動の分析**: LangChainを使用した企業分析と要件抽出
- 📊 **RAG統合**: Chromaベクトルストアによる過去の求人情報の活用
- 🎨 **直感的なUI**: Streamlitによる使いやすいインターフェース
- 📄 **PDF出力**: reportlabによる美しいPDF生成
- 🔄 **反復改善**: フィードバックに基づく改善機能

## アーキテクチャ

```
resume-ai/
├── agents/              # 各種エージェント実装
│   ├── company_analysis_agent.py
│   ├── requirements_extraction_agent.py
│   ├── resume_structure_agent.py
│   ├── resume_generation_agent.py
│   └── feedback_improvement_agent.py
├── prompts/            # プロンプトテンプレート
├── rag/                # RAG層（Chroma）
├── pdf/                # PDF生成
├── ui/                 # Streamlit UI
├── orchestrator/       # エージェントオーケストレーション
├── models/             # データモデル
└── app.py              # メインアプリケーション
```

## 必要要件

- Python 3.10以上
- OpenAI APIキー

## インストール

1. リポジトリをクローン:
```bash
git clone https://github.com/urabe-chihiro/resume-ai.git
cd resume-ai
```

2. 依存パッケージをインストール:
```bash
pip install -r requirements.txt
```

3. 環境変数を設定:
```bash
cp .env.example .env
# .envファイルを編集してOpenAI APIキーを設定
```

## 使い方

1. アプリケーションを起動:
```bash
streamlit run app.py
```

2. ブラウザが自動的に開きます（通常は http://localhost:8501）

3. UIで以下の情報を入力:
   - 個人情報（氏名、連絡先）
   - 職務経歴
   - 学歴
   - スキル
   - 応募する企業・求人情報

4. 「職務経歴書を生成」ボタンをクリック

5. 生成された職務経歴書を確認し、必要に応じて改善フィードバックを入力

6. Markdown形式またはPDF形式でダウンロード

## 処理フロー

```
[ユーザー入力]
   ↓
[入力正規化・検証]
   ↓
[RAG層 (Chroma)] ── 募集要項 / 企業情報 / ユーザー経歴
   ↓
[Agent Orchestrator]
   ├─ 企業分析Agent
   ├─ 要件抽出Agent
   ├─ 職務経歴書構成Agent
   ├─ 職務経歴書生成Agent
   └─ 改善・フィードバック反映Agent
   ↓
[職務経歴書 Markdown]
   ↓
[PDF生成]
   ↓
[ダウンロード]
```

## 技術スタック

- **LangChain**: LLMオーケストレーション
- **OpenAI GPT-4**: テキスト生成
- **Chroma**: ベクトルデータベース（RAG）
- **Streamlit**: Webアプリケーションフレームワーク
- **reportlab**: PDF生成
- **Pydantic**: データバリデーション

## ライセンス

MIT License

## 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずissueを開いて変更内容を議論してください。