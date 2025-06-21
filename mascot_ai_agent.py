import sys
import json
import os
import operator
import asyncio
from dotenv import load_dotenv, find_dotenv
from typing_extensions import TypedDict, Annotated
from typing import Any, List

from qasync import QApplication, QEventLoop, asyncSlot
from PyQt6.QtWidgets import (QWidget, QLabel, QVBoxLayout,
                             QLineEdit, QScrollArea, QSizePolicy)
from PyQt6.QtGui import QMovie, QPixmap, QPainter, QMouseEvent, QFont
from PyQt6.QtCore import Qt, QPoint, QSize, QTimer

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_mcp_adapters.client import MultiServerMCPClient

CHARACTER_GIF_PATH = "shiba_hie.gif"
TARGET_CHARACTER_WIDTH = 150
FIXED_INTERACTION_HEIGHT = 100
BUBBLE_PADDING = 10

_ = load_dotenv(find_dotenv())
GOOGLE_API_KEY = os.getenv("GOOGLE_APIKEY")

class GraphState(TypedDict):
    messages: Annotated[list[AnyMessage], operator.add]

def create_lang_graph(tools, model_chain):
    def should_continue(state: GraphState):
        messages = state["messages"]
        last_message = messages[-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"

        return END

    def call_model(state: GraphState):
        messages = state["messages"]
        response = model_chain.invoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)
    
    workflow = StateGraph(GraphState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, ["tools", END])
    workflow.add_edge("tools", "agent")
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app

class MascotWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.offset = QPoint()
        self.is_dragging = False
        
        self.graph = None
        self.graph_config = {"configurable": {"thread_id": "mascot_chat_1"}}
        self.ai_processing = False

        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.character_label = QLabel(self)
        self.movie = QMovie(CHARACTER_GIF_PATH)

        char_display_width = TARGET_CHARACTER_WIDTH
        char_display_height = TARGET_CHARACTER_WIDTH

        if not self.movie.isValid():
            print(f"エラー: GIFファイル '{CHARACTER_GIF_PATH}' を読み込めません。")
            char_display_height = int(TARGET_CHARACTER_WIDTH * 0.75)
            self.character_label.setStyleSheet(f"background-color: rgba(100, 100, 255, 180); border-radius: 10px;")
        else:
            self.movie.jumpToFrame(0)
            original_char_size = self.movie.currentPixmap().size()
            original_width = original_char_size.width()
            original_height = original_char_size.height()

            if original_width > 0 and original_height > 0:
                aspect_ratio = original_height / original_width
                char_display_height = int(char_display_width * aspect_ratio)
            else:
                char_display_height = int(TARGET_CHARACTER_WIDTH * 0.75)

            self.movie.setScaledSize(QSize(char_display_width, char_display_height))
            self.character_label.setMovie(self.movie)
            self.movie.start()

        self.character_label.setFixedSize(char_display_width, char_display_height)
        self.character_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.character_label)

        self.interaction_widget = QWidget(self)
        self.interaction_widget.setFixedWidth(char_display_width)
        self.interaction_widget.setFixedHeight(FIXED_INTERACTION_HEIGHT)

        interaction_layout = QVBoxLayout(self.interaction_widget)
        interaction_layout.setContentsMargins(0, 0, 0, BUBBLE_PADDING // 2)
        interaction_layout.setSpacing(BUBBLE_PADDING // 2)

        self.bubble_label_content = QLabel("こんにちは！", self)
        self.bubble_label_content.setWordWrap(True)
        self.bubble_label_content.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        bubble_font = QFont()
        bubble_font.setPointSize(12)
        self.bubble_label_content.setFont(bubble_font)
        
        self.bubble_label_content.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                color: black;
                padding: {BUBBLE_PADDING}px;
            }}
        """)
        self.bubble_label_content.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.MinimumExpanding)

        self.bubble_scroll_area = QScrollArea(self.interaction_widget)
        self.bubble_scroll_area.setWidget(self.bubble_label_content)
        self.bubble_scroll_area.setWidgetResizable(True)
        self.bubble_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.bubble_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.bubble_scroll_area.setStyleSheet(f"""
            QScrollArea {{
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #ccc;
                border-radius: 10px;
            }}
            QScrollBar:vertical {{
                border: none;
                background: rgba(220, 220, 220, 150);
                width: 8px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: rgba(150, 150, 150, 200);
                min-height: 20px;
                border-radius: 4px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0px; background: none; }}
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {{ background: none; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
        """)
        interaction_layout.addWidget(self.bubble_scroll_area, 1)

        self.input_field = QLineEdit(self.interaction_widget)
        self.input_field.setPlaceholderText("AIを準備中...")
        self.input_field.setEnabled(False)

        input_font = QFont()
        input_font.setPointSize(12)
        self.input_field.setFont(input_font)
        self.input_field.setFixedHeight(30)

        self.input_field.setStyleSheet("border: 1px solid #ccc; border-radius: 5px; padding: 5px; background-color: white;")
        interaction_layout.addWidget(self.input_field)

        self.input_field.returnPressed.connect(self.handle_user_input)

        self.main_layout.addWidget(self.interaction_widget)
        self.setLayout(self.main_layout)

        total_width = char_display_width
        total_height = char_display_height + FIXED_INTERACTION_HEIGHT

        self.setGeometry(100, 100, total_width, total_height)
        self.setFixedSize(total_width, total_height)

        self.show()

    @asyncSlot()
    async def init_ai_backend(self):
        """
        LangGraph と AI モデルの初期化を行う非同期関数。
        """
        self.update_bubble("AIを準備中...")
        try:
            model = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=GOOGLE_API_KEY,
                temperature=0.001,
            )

            with open("mcp_config.json", "r") as f:
                mcp_config = json.load(f)

            mcp_client = MultiServerMCPClient(mcp_config["mcpServers"])
            tools = await mcp_client.get_tools()

            message_prompt = [
                SystemMessage(content="""
あなたは役にたつAIアシスタントです。日本語で回答し、考えた過程を結論より前に出力してください。
あなたは、「PlayWrite」というブラウザを操作するtoolと「Filesystem」というローカル環境のファイル操作をするtoolを利用することができます。適切に利用してユーザからの質問に回答してください。
ツールを利用する場合は、必ずツールから得られた情報のみを利用して回答してください。「Filesystem」を使ってファイルを保存するときのパスは/Users/yourname/path/test配下です。

まず、ユーザの質問からツールをどういう意図で何回利用しないといけないのかを判断し、必要なら複数回toolを利用して情報収集をしたのち、すべての情報が取得できたら、その情報を元に返答してください。

なお、サイトのアクセスでエラーが出た場合は、もう一度再施行してください。ネットワーク関連のエラーの場合があります。
                """),
                MessagesPlaceholder("messages"),
            ]

            prompt = ChatPromptTemplate.from_messages(message_prompt)
            model_with_tools = prompt | model.bind_tools(tools)

            self.graph = create_lang_graph(
                tools,
                model_with_tools
            )
            self.update_bubble("準備完了！話しかけてください。")
            self.input_field.setPlaceholderText("AIに話しかけてね...")
            self.input_field.setEnabled(True)

        except Exception as e:
            error_msg = f"AIの初期化中にエラーが発生しました: {e}"
            print(error_msg)
            self.update_bubble(error_msg)
            self.input_field.setEnabled(False)
            self.input_field.setPlaceholderText("初期化エラー")

    def update_bubble(self, text):
        """
        吹き出しのテキストを更新し、スクロール位置を調整する。
        """
        current_text = self.bubble_label_content.text()
        if current_text:
            new_text = f"{current_text}\n\n{text}"
        else:
            new_text = text
            
        self.bubble_label_content.setText(new_text)

        QTimer.singleShot(10, lambda: self.bubble_scroll_area.verticalScrollBar().setValue(self.bubble_scroll_area.verticalScrollBar().maximum()))

    @asyncSlot()
    async def handle_user_input(self):
        """
        ユーザーの入力を処理し、AIに渡す。
        """
        user_text = self.input_field.text()
        if not user_text or self.ai_processing:
            return
        
        self.input_field.clear()
        self.update_bubble(f"あなた: {user_text}")
        self.update_bubble("AI: 考え中...")
        self.input_field.setEnabled(False)
        self.ai_processing = True

        try:
            ai_response = await self.process_with_ai(user_text)
            self.update_bubble(f"AI: {ai_response}")
        except Exception as e:
            error_msg = f"AI応答の取得中にエラーが発生しました: {e}"
            print(error_msg)
            self.update_bubble(error_msg)
        finally:
            self.input_field.setEnabled(True)
            self.ai_processing = False

    async def process_with_ai(self, user_text):
        """
        LangGraph を使用してAIからの応答を取得する非同期関数。
        """
        if not self.graph:
            return "AIがまだ準備できていません。"

        try:
            input_query = [HumanMessage(
                [
                    {
                        "type": "text",
                        "text": f"{user_text}"
                    },
                ]
            )]
            response = await self.graph.ainvoke(
                {"messages": input_query}, 
                {
                    **self.graph_config,
                    "recursion_limit": 50
                }
            )
            return response["messages"][-1].content
        except Exception as e:
            print(f"LangGraph実行中にエラー: {e}")
            return f"AI内部でエラーが発生しました: {e}"

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.character_label.geometry().contains(event.pos()) or \
               (self.interaction_widget.geometry().contains(event.pos()) and \
                event.pos().y() < self.interaction_widget.y() + BUBBLE_PADDING * 2 + self.input_field.height()):
                self.is_dragging = True
                self.offset = event.globalPosition().toPoint() - self.pos()
                event.accept()
            else:
                event.ignore()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.offset)
            event.accept()
        else:
            event.ignore()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            event.accept()
        else:
            event.ignore()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    mascot = MascotWidget()

    async def run_mascot_app():
        await mascot.init_ai_backend()

    with loop:
        loop.create_task(run_mascot_app())
        loop.run_forever()