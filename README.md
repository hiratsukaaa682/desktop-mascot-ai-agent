# 🐶 AIエージェント × MCP で実現するデスクトップマスコット

これは、Gemini API × LangGraph × MCPを使った、インタラクティブなデスクトップAIマスコットアプリです。可愛い犬のキャラクターと自然言語で会話しながら、ブラウザ操作やファイル管理などの実行をAIエージェントに「丸投げ」できます。

---

## 📹 デモ



---

## 🔧 機能概要

- 🧠 **AIとの会話**：自然言語で話しかけると、AIが理解し応答します。
- 🌐 **ブラウザ操作（Playwright MCP）**：スクレイピング・検索・ページ遷移などをAIが自動実行。
- 📁 **ファイル操作（Filesystem MCP）**：指定パスにファイル保存や読み取りも可能。
- 💬 **LangGraph対応**：会話の履歴・状態管理に対応、マルチツールの制御もスマート。
- 🐕 **デスクトップに常駐するマスコットUI**：吹き出しや入力欄つきのPyQt6 + QMovie UI。

---

## 🚀 動作環境

- Python 3.13（※ 他のバージョンは未確認）
- macOS m1（※ Windows / Linuxは未確認）
- .envファイルに [Google AI Studio](https://aistudio.google.com/) のGemini APIキーを設定

---

## 📦 セットアップ手順

1. リポジトリをクローン
```bash
git clone https://github.com/hiratsukaaa682/desktop-mascot-ai-agent.git
cd desktop-mascot-ai-agent
```

1.	依存関係をインストール
```bash
pip install -r requirements.txt
```

1.	.env に Gemini API キーを設定
```
GOOGLE_APIKEY="your_apikey"
```

---

## 実行方法

python mascot_ai_agent.py

初回実行時、マスコットが「AIを準備中…」と表示します。起動後、自由に話しかけてください！

---

⚠️ 注意事項
- このアプリはデスクトップ常駐型ですが、デスクトップアプリにはなっていません。
- Gemini APIは別途準備・設定が必要です。
- GUIサイズ・位置は固定（移動可能）、終了機能などは別途追加が必要です。

---

📝 ライセンス

MIT License
