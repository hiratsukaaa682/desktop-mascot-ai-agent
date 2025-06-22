# 🐶 Desktop Mascot AI Agent using Gemini API × LangGraph × MCP

This is an interactive desktop mascot AI agent powered by **Gemini API × LangGraph × MCP**.  
You can communicate with a cute dog character in natural language and delegate tasks like browser automation and file management.

---

## 📹 Demo

https://github.com/user-attachments/assets/1f9a8738-054b-4321-887c-f69da7ffac25

The agent can operate the browser and file system autonomously based on user instructions.

It can even search for relevant websites without being given exact URLs. In the demo, some URLs in the CSV file aren't fully written out, but the agent still works well with a bit of prompt tuning.

---

## 🔧 Features

- 🧠 **Conversational AI**: Talk to the agent naturally; it understands and responds accordingly.
- 🌐 **Browser automation (Playwright MCP)**: Automatically performs web scraping, search, navigation, and more.
- 📁 **File operations (Filesystem MCP)**: Reads from and saves to specified paths via AI.
- 💬 **LangGraph integration**: Manages conversational state and controls multiple tools intelligently.
- 🐕 **Always-on desktop mascot UI**: PyQt6 + QMovie-based UI with dialog bubbles and an input field.

---

## 🚀 Requirements

- Python 3.13 (other versions untested)
- Node.js v24.2.0 (other versions untested)
- Tested on:
  - MacBook Air M1
  - macOS Sequoia  
    *(Windows/Linux not tested)*

---

## 📦 Setup

1. Clone the repository:
    ```bash
    git clone https://github.com/hiratsukaaa682/desktop-mascot-ai-agent.git
    cd desktop-mascot-ai-agent
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up MCP servers:
    ```bash
    # Playwright MCP
    npx @playwright/mcp@latest

    # Filesystem MCP
    npm install -g @modelcontextprotocol/server-filesystem
    ```

4. Add your Gemini API key to the `.env` file:
    ```
    GOOGLE_APIKEY="your_apikey"
    ```

---

## 🏃 How to Run

```bash
python mascot_ai_agent.py

On the first launch, the mascot will say “Preparing AI…”. Once it’s ready, feel free to start chatting!

⸻

## ⚠️ Notes
- This app runs persistently on your desktop but is not packaged as a standalone desktop app.
- Gemini API setup is required separately.
- GUI size and position are fixed (movable), and shutdown functionality needs to be added manually.

⸻

## 📄 License

This project is licensed under the MIT License – see the LICENSE.md file for details.
