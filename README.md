# 🐶 AIエージェント × MCP で実現するデスクトップマスコット

これは、Gemini API × LangGraph × MCPを使った、インタラクティブなデスクトップマスコットAIエージェントです。可愛い犬のキャラクターと自然言語で会話しながら、ブラウザ操作やファイル管理などの実行をAIエージェントに「丸投げ」できます。

---

## 📹 デモ

https://github.com/user-attachments/assets/1f9a8738-054b-4321-887c-f69da7ffac25

このように自らブラウザやファイルを操作し、ユーザの指示に応えてくれます。

調子がいい時は情報を取得しに行くWebサイトのURLを指定しなくても探しに行ってくれます。また、デモではCSVファイルに含まれるURLがフルリンクになっていないのですが、このあたりはプロンプトを調整することでうまく機能すると思います。

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
- Node.js v24.2.0（他のバージョンは未確認）
- Macbook Air M1
  - macOS Sequoia（※ Windows / Linuxは未確認）

---

## 📦 セットアップ手順
1. リポジトリをクローン
    ```bash
    git clone https://github.com/hiratsukaaa682/desktop-mascot-ai-agent.git
    cd desktop-mascot-ai-agent
    ```
1. 依存関係をインストール
    ```bash
    pip install -r requirements.txt
    ```
1. MCP Serverを使えるようにする
    ```bash
    # Playwright MCP
    # 何も表示されなければOKです。
    npx @playwright/mcp@latest

    # Filesystem MCP
    npm install -g @modelcontextprotocol/server-filesystem
    ```
1. .env に Gemini API キーを設定
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
