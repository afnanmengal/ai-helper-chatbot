"""
Afnan's AI - Futuristic Desktop Neural Assistant.
Sleek cyberpunk dark-mode GUI with GPU/CPU mode toggle and zero hardware clutter.
"""

import sys
import os
import json
import datetime
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer

from core.client import OllamaClient
from core.personas import PERSONAS, DEFAULT_PERSONA
from core.config import AppConfig
from core.database import DatabaseManager

# Futuristic Cyberpunk / Glassmorphic Theme
STYLESHEET = """
QMainWindow {
    background-color: #060810;
}

QWidget {
    font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif;
    color: #E2E8F0;
    font-size: 13px;
}

QSplitter::handle {
    background-color: #121829;
    width: 2px;
}

/* Sidebar */
#sidebar {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #0B0E19, stop:1 #060812);
    border-right: 1px solid #161D33;
}

#logoTitle {
    font-size: 21px;
    font-weight: 800;
    color: #00F0FF;
    letter-spacing: 1.5px;
}

#logoSubtitle {
    font-size: 10px;
    font-weight: 700;
    color: #818CF8;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

#sectionHeader {
    font-size: 10px;
    font-weight: 800;
    color: #38BDF8;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-top: 10px;
    margin-bottom: 4px;
}

/* Futuristic Status Card (No raw hardware specs) */
#statusCard {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0F1426, stop:1 #0A0D1B);
    border: 1px solid #1E2749;
    border-radius: 9px;
    padding: 10px 12px;
    margin-bottom: 6px;
}

#statusTitle {
    font-size: 11px;
    font-weight: 700;
    color: #00F0FF;
    letter-spacing: 1px;
}

#statusBadge {
    font-size: 11px;
    font-weight: 600;
    color: #10B981;
}

/* Form Controls */
QComboBox, QLineEdit, QSpinBox, QSlider {
    background-color: #0E1324;
    border: 1px solid #1D2644;
    border-radius: 7px;
    padding: 7px 10px;
    color: #F1F5F9;
}

QComboBox:hover, QLineEdit:focus {
    border: 1px solid #00F0FF;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #0C1020;
    border: 1px solid #1D2644;
    selection-background-color: #2E1065;
    selection-color: #00F0FF;
    color: #F1F5F9;
}

QPushButton {
    background-color: #141A33;
    color: #F8FAFC;
    border: 1px solid #242E57;
    border-radius: 7px;
    padding: 7px 12px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #1C2447;
    border: 1px solid #00F0FF;
    color: #00F0FF;
}

QPushButton#newChatBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:1 #6366F1);
    border: none;
    color: #060810;
    font-weight: 800;
    padding: 9px 14px;
    border-radius: 8px;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

QPushButton#newChatBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38BDF8, stop:1 #818CF8);
    color: #000000;
}

QPushButton#sendBtn {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00F0FF, stop:1 #7C3AED);
    border: none;
    color: #060810;
    font-weight: 800;
    padding: 9px 20px;
    border-radius: 8px;
    letter-spacing: 1px;
}

QPushButton#sendBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #38BDF8, stop:1 #9333EA);
}

QPushButton#stopBtn {
    background: #DC2626;
    border: none;
    color: #FFFFFF;
    font-weight: 700;
    padding: 9px 18px;
    border-radius: 8px;
}

QPushButton#stopBtn:hover {
    background: #B91C1C;
}

/* Session History Vault */
#sessionList {
    background-color: #090C19;
    border: 1px solid #161D36;
    border-radius: 8px;
    padding: 4px;
    color: #CBD5E1;
    font-size: 12px;
}

#sessionList::item {
    padding: 7px 9px;
    border-radius: 6px;
    margin-bottom: 2px;
}

#sessionList::item:hover {
    background-color: #12182F;
    color: #00F0FF;
}

#sessionList::item:selected {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #1E1B4B, stop:1 #312E81);
    border: 1px solid #6366F1;
    color: #00F0FF;
    font-weight: 700;
}

/* Chat Area */
#chatContainer {
    background-color: #060810;
}

#chatScroll {
    border: none;
    background-color: transparent;
}

/* Input Area */
#inputFrame {
    background-color: #090C18;
    border-top: 1px solid #161D36;
    padding: 12px 16px;
}

#promptInput {
    background-color: #0E1325;
    border: 1px solid #1F284A;
    border-radius: 9px;
    padding: 10px 12px;
    color: #F8FAFC;
    font-size: 13px;
}

#promptInput:focus {
    border: 1px solid #00F0FF;
}

QScrollBar:vertical {
    border: none;
    background: #060810;
    width: 6px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #1B233D;
    min-height: 20px;
    border-radius: 3px;
}

QScrollBar::handle:vertical:hover {
    background: #00F0FF;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""

class ChatWorker(QThread):
    """Background worker for streaming LLM tokens smoothly."""
    token_received = pyqtSignal(str)
    finished_stream = pyqtSignal(str)
    error_occurred = pyqtSignal(str)

    def __init__(self, client: OllamaClient, messages: list, model: str, temperature: float, num_ctx: int, gpu_layers: int):
        super().__init__()
        self.client = client
        self.messages = messages
        self.model = model
        self.temperature = temperature
        self.num_ctx = num_ctx
        self.gpu_layers = gpu_layers
        self.full_response = ""

    def run(self):
        try:
            for token in self.client.chat_stream(
                messages=self.messages,
                model=self.model,
                temperature=self.temperature,
                num_ctx=self.num_ctx,
                gpu_layers=self.gpu_layers
            ):
                self.full_response += token
                self.token_received.emit(token)
            self.finished_stream.emit(self.full_response)
        except Exception as e:
            self.error_occurred.emit(str(e))

class ModelDownloadWorker(QThread):
    """Background worker for pulling models with progress reporting."""
    progress_updated = pyqtSignal(str, float)
    download_finished = pyqtSignal(str, bool)

    def __init__(self, client: OllamaClient, model_name: str):
        super().__init__()
        self.client = client
        self.model_name = model_name

    def run(self):
        try:
            for item in self.client.pull_model_stream(self.model_name):
                status = item.get("status", "")
                pct = item.get("percent", 0.0)
                self.progress_updated.emit(status, pct)
            self.download_finished.emit(self.model_name, True)
        except Exception as e:
            self.download_finished.emit(str(e), False)

class ChatBubble(QtWidgets.QFrame):
    """Futuristic message bubble for user and Afnan's AI responses."""
    def __init__(self, role: str, text: str, persona_name: str = ""):
        super().__init__()
        self.role = role
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(6)

        # Header with role & timestamp
        header_layout = QtWidgets.QHBoxLayout()
        header_label = QtWidgets.QLabel()
        time_str = datetime.datetime.now().strftime("%I:%M %p")
        
        if role == "user":
            header_label.setText(f"👤 <b>YOU</b> • {time_str}")
            header_label.setStyleSheet("color: #A5B4FC; font-size: 11px; font-weight: 700; letter-spacing: 0.5px;")
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E1B4B, stop:1 #110E2E);
                    border: 1px solid #4338CA;
                    border-radius: 12px;
                    margin-left: 70px;
                    margin-right: 10px;
                    margin-bottom: 8px;
                }
            """)
        else:
            p_tag = f" // {persona_name}" if persona_name else ""
            header_label.setText(f"✦ <b>AFNAN'S AI{p_tag}</b> • {time_str}")
            header_label.setStyleSheet("color: #00F0FF; font-size: 11px; font-weight: 800; letter-spacing: 1px;")
            self.setStyleSheet("""
                QFrame {
                    background-color: #0B0F1E;
                    border-left: 3px solid #00F0FF;
                    border-top: 1px solid #18213D;
                    border-right: 1px solid #18213D;
                    border-bottom: 1px solid #18213D;
                    border-radius: 12px;
                    margin-left: 10px;
                    margin-right: 70px;
                    margin-bottom: 8px;
                }
            """)

        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Copy button for Assistant messages
        if role != "user":
            copy_btn = QtWidgets.QPushButton("📋 Copy")
            copy_btn.setFixedSize(60, 22)
            copy_btn.setStyleSheet("""
                QPushButton {
                    background: #141A33;
                    border: 1px solid #202A4E;
                    border-radius: 4px;
                    font-size: 10px;
                    padding: 2px 6px;
                    color: #94A3B8;
                }
                QPushButton:hover {
                    background: #1E284E;
                    border: 1px solid #00F0FF;
                    color: #00F0FF;
                }
            """)
            copy_btn.clicked.connect(self.copy_content)
            header_layout.addWidget(copy_btn)

        layout.addLayout(header_layout)

        # Content text label (supports rich text/markdown)
        self.text_label = QtWidgets.QTextBrowser()
        self.text_label.setOpenExternalLinks(True)
        self.text_label.setReadOnly(True)
        self.text_label.setStyleSheet("""
            QTextBrowser {
                background: transparent;
                border: none;
                color: #F1F5F9;
                font-size: 13px;
                line-height: 1.5;
                selection-background-color: #4F46E5;
            }
        """)
        self.text_label.setMarkdown(text)
        self.text_label.document().adjustSize()
        layout.addWidget(self.text_label)
        self.raw_text = text

    def update_text(self, text: str):
        self.raw_text = text
        self.text_label.setMarkdown(text)

    def copy_content(self):
        QtWidgets.QApplication.clipboard().setText(self.raw_text)

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Afnan's AI • Autonomous Neural Assistant")
        self.resize(1150, 780)
        self.setMinimumSize(880, 620)
        self.setStyleSheet(STYLESHEET)

        self.config = AppConfig()
        self.client = OllamaClient(self.config.ollama_host)
        self.db = DatabaseManager()
        self.current_session_id = None
        self.conversation_history = []
        self.current_worker = None
        self.current_bubble = None

        # Restore saved compute mode preference (default: GPU Mode)
        saved_mode = self.db.get_setting("compute_mode", "gpu")
        self.is_cpu_mode = (saved_mode == "cpu")

        self.init_ui()
        self.refresh_models()
        self.load_or_create_session()

    def init_ui(self):
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QtWidgets.QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter between Sidebar and Chat Area
        splitter = QtWidgets.QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.build_sidebar())
        splitter.addWidget(self.build_chat_area())
        splitter.setSizes([310, 840])
        splitter.setCollapsible(0, False)
        main_layout.addWidget(splitter)

    def build_sidebar(self) -> QtWidgets.QWidget:
        sidebar = QtWidgets.QWidget()
        sidebar.setObjectName("sidebar")
        layout = QtWidgets.QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(8)

        # Branding: Afnan's AI
        title = QtWidgets.QLabel("✦ AFNAN'S AI")
        title.setObjectName("logoTitle")
        subtitle = QtWidgets.QLabel("AUTONOMOUS NEURAL ASSISTANT")
        subtitle.setObjectName("logoSubtitle")
        layout.addWidget(title)
        layout.addWidget(subtitle)

        # ➕ New Conversation Button
        new_chat_btn = QtWidgets.QPushButton("➕ NEW CONVERSATION")
        new_chat_btn.setObjectName("newChatBtn")
        new_chat_btn.clicked.connect(self.create_new_session)
        layout.addWidget(new_chat_btn)

        # Saved Conversations (Database Vault)
        hist_hdr = QtWidgets.QLabel("// CONVERSATION VAULT")
        hist_hdr.setObjectName("sectionHeader")
        layout.addWidget(hist_hdr)

        self.session_list = QtWidgets.QListWidget()
        self.session_list.setObjectName("sessionList")
        self.session_list.setMaximumHeight(130)
        self.session_list.itemClicked.connect(self.on_session_selected)
        layout.addWidget(self.session_list)

        # Futuristic Neural Status Card (No system hardware specs)
        status_card = QtWidgets.QFrame()
        status_card.setObjectName("statusCard")
        status_layout = QtWidgets.QVBoxLayout(status_card)
        status_layout.setContentsMargins(10, 8, 10, 8)
        status_layout.setSpacing(4)

        self.status_title = QtWidgets.QLabel("SYSTEM CORE")
        self.status_title.setObjectName("statusTitle")
        
        self.status_badge = QtWidgets.QLabel("● NEURAL LINK: ACTIVE")
        self.status_badge.setObjectName("statusBadge")
        
        self.engine_mode_lbl = QtWidgets.QLabel("⚡ ACCELERATION: GPU")
        self.engine_mode_lbl.setStyleSheet("color: #38BDF8; font-size: 11px; font-weight: 700;")

        status_layout.addWidget(self.status_title)
        status_layout.addWidget(self.status_badge)
        status_layout.addWidget(self.engine_mode_lbl)
        layout.addWidget(status_card)

        # Compute Mode Selector: GPU vs CPU Mode
        comp_hdr = QtWidgets.QLabel("// COMPUTE ENGINE")
        comp_hdr.setObjectName("sectionHeader")
        layout.addWidget(comp_hdr)

        self.compute_combo = QtWidgets.QComboBox()
        self.compute_combo.addItem("🚀 GPU Mode (Accelerated)", "gpu")
        self.compute_combo.addItem("💻 CPU Mode (Universal / Low Power)", "cpu")
        if self.is_cpu_mode:
            self.compute_combo.setCurrentIndex(1)
        self.compute_combo.currentIndexChanged.connect(self.on_compute_mode_changed)
        layout.addWidget(self.compute_combo)

        # Persona Selector Section
        p_hdr = QtWidgets.QLabel("// NEURAL PERSONA")
        p_hdr.setObjectName("sectionHeader")
        layout.addWidget(p_hdr)

        self.persona_combo = QtWidgets.QComboBox()
        for p_name in PERSONAS.keys():
            self.persona_combo.addItem(p_name)
        self.persona_combo.setCurrentText(DEFAULT_PERSONA)
        self.persona_combo.currentIndexChanged.connect(self.on_persona_changed)
        layout.addWidget(self.persona_combo)

        self.persona_desc = QtWidgets.QLabel(PERSONAS[DEFAULT_PERSONA]["description"])
        self.persona_desc.setWordWrap(True)
        self.persona_desc.setStyleSheet("color: #94A3B8; font-size: 11px; margin-bottom: 2px;")
        layout.addWidget(self.persona_desc)

        # Model Selector Section
        m_hdr = QtWidgets.QLabel("// ACTIVE MODEL")
        m_hdr.setObjectName("sectionHeader")
        layout.addWidget(m_hdr)

        model_row = QtWidgets.QHBoxLayout()
        self.model_combo = QtWidgets.QComboBox()
        refresh_btn = QtWidgets.QPushButton("🔄")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.setToolTip("Refresh models")
        refresh_btn.clicked.connect(self.refresh_models)
        model_row.addWidget(self.model_combo, 1)
        model_row.addWidget(refresh_btn)
        layout.addLayout(model_row)

        # Generation Parameters
        param_hdr = QtWidgets.QLabel("// PARAMETERS")
        param_hdr.setObjectName("sectionHeader")
        layout.addWidget(param_hdr)

        temp_row = QtWidgets.QHBoxLayout()
        temp_row.addWidget(QtWidgets.QLabel("Creativity:"))
        self.temp_slider = QtWidgets.QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(1, 10)
        self.temp_slider.setValue(7)
        self.temp_val_lbl = QtWidgets.QLabel("0.7")
        self.temp_slider.valueChanged.connect(lambda v: self.temp_val_lbl.setText(f"{v/10:.1f}"))
        temp_row.addWidget(self.temp_slider)
        temp_row.addWidget(self.temp_val_lbl)
        layout.addLayout(temp_row)

        ctx_row = QtWidgets.QHBoxLayout()
        ctx_row.addWidget(QtWidgets.QLabel("Context Limit:"))
        self.ctx_combo = QtWidgets.QComboBox()
        self.ctx_combo.addItems(["1024 tokens", "2048 tokens", "4096 tokens"])
        self.ctx_combo.setCurrentIndex(1)
        ctx_row.addWidget(self.ctx_combo)
        layout.addLayout(ctx_row)

        layout.addStretch()

        # Action Buttons (Delete Chat / Export)
        actions_row = QtWidgets.QHBoxLayout()
        del_btn = QtWidgets.QPushButton("🗑️ Delete")
        del_btn.clicked.connect(self.delete_current_session)
        export_btn = QtWidgets.QPushButton("💾 Export")
        export_btn.clicked.connect(self.export_chat)
        actions_row.addWidget(del_btn)
        actions_row.addWidget(export_btn)
        layout.addLayout(actions_row)

        self.update_compute_badge()
        return sidebar

    def build_chat_area(self) -> QtWidgets.QWidget:
        chat_widget = QtWidgets.QWidget()
        chat_widget.setObjectName("chatContainer")
        layout = QtWidgets.QVBoxLayout(chat_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll Area for Messages
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setObjectName("chatScroll")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.messages_container = QtWidgets.QWidget()
        self.messages_layout = QtWidgets.QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 16, 20, 16)
        self.messages_layout.setSpacing(6)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        layout.addWidget(self.scroll_area, 1)

        # Input Frame at the bottom
        input_frame = QtWidgets.QFrame()
        input_frame.setObjectName("inputFrame")
        input_layout = QtWidgets.QHBoxLayout(input_frame)
        input_layout.setContentsMargins(16, 12, 16, 12)
        input_layout.setSpacing(10)

        self.prompt_input = QtWidgets.QTextEdit()
        self.prompt_input.setObjectName("promptInput")
        self.prompt_input.setPlaceholderText("Ask Afnan's AI anything... (Press Shift+Enter for new line, Enter to Send)")
        self.prompt_input.setMaximumHeight(85)
        self.prompt_input.installEventFilter(self)
        input_layout.addWidget(self.prompt_input, 1)

        # Buttons on the right: Send / Stop
        btn_layout = QtWidgets.QVBoxLayout()
        self.send_btn = QtWidgets.QPushButton("TRANSMIT 🚀")
        self.send_btn.setObjectName("sendBtn")
        self.send_btn.clicked.connect(self.send_message)
        
        self.stop_btn = QtWidgets.QPushButton("HALT ⏹")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.clicked.connect(self.stop_generation)
        self.stop_btn.setVisible(False)

        btn_layout.addWidget(self.send_btn)
        btn_layout.addWidget(self.stop_btn)
        input_layout.addLayout(btn_layout)

        layout.addWidget(input_frame)
        return chat_widget

    def add_welcome_message(self):
        welcome_md = (
            "### ✦ Greetings! I am Afnan's AI.\n\n"
            "I am your personal autonomous neural assistant. How can I help you today?\n\n"
            "**Core Capabilities:**\n"
            "- 💡 **Inquiry & Brainstorming:** Instant answers, deep breakdowns, conceptual clarity.\n"
            "- 💻 **Code & Engineering:** Python, C++, ML pipelines, syntax debugging, architecture.\n"
            "- 📝 **Writing & Synthesis:** Technical briefs, executive emails, essay structuring.\n\n"
            "*Choose a neural persona on the left or enter your question below.*"
        )
        bubble = ChatBubble("assistant", welcome_md, "Neural Core")
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)

    def on_compute_mode_changed(self):
        mode = self.compute_combo.currentData()
        self.is_cpu_mode = (mode == "cpu")
        self.db.set_setting("compute_mode", mode)
        self.update_compute_badge()

    def update_compute_badge(self):
        if self.is_cpu_mode:
            self.engine_mode_lbl.setText("💻 ENGINE: CPU MODE (UNIVERSAL)")
            self.engine_mode_lbl.setStyleSheet("color: #A78BFA; font-size: 11px; font-weight: 700;")
        else:
            self.engine_mode_lbl.setText("⚡ ENGINE: GPU ACCELERATED")
            self.engine_mode_lbl.setStyleSheet("color: #00F0FF; font-size: 11px; font-weight: 700;")

    def eventFilter(self, obj, event):
        """Allows Enter to send and Shift+Enter for new line."""
        if obj == self.prompt_input and event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self.send_message()
                return True
        return super().eventFilter(obj, event)

    def on_persona_changed(self):
        selected = self.persona_combo.currentText()
        if selected in PERSONAS:
            self.persona_desc.setText(PERSONAS[selected]["description"])

    def refresh_models(self):
        self.client.ensure_server_running()
        models = self.client.list_models()
        self.model_combo.clear()
        if models:
            self.model_combo.addItems(models)
            for m in ["qwen2.5:0.5b", "llama3.2:1b", "qwen2.5:1.5b"]:
                idx = self.model_combo.findText(m, Qt.MatchFlag.MatchContains)
                if idx >= 0:
                    self.model_combo.setCurrentIndex(idx)
                    break
        else:
            self.model_combo.addItem(self.config.default_model)

    def load_or_create_session(self):
        sessions = self.db.get_sessions()
        if sessions:
            first_sid = sessions[0]["id"]
            self.current_session_id = first_sid
            self.refresh_session_list()
            self.load_session_messages(first_sid)
        else:
            self.create_new_session()

    def create_new_session(self):
        persona = self.persona_combo.currentText()
        model = self.model_combo.currentText() or self.config.default_model
        sid = self.db.create_session("New Conversation", persona=persona, model=model)
        self.current_session_id = sid
        self.conversation_history.clear()
        self.clear_chat_widgets()
        self.add_welcome_message()
        self.refresh_session_list()

    def refresh_session_list(self):
        self.session_list.blockSignals(True)
        self.session_list.clear()
        sessions = self.db.get_sessions(limit=30)
        for s in sessions:
            t = s["title"]
            if len(t) > 26:
                t = t[:24] + "..."
            item = QtWidgets.QListWidgetItem(f"✦ {t}")
            item.setData(Qt.ItemDataRole.UserRole, s["id"])
            item.setToolTip(f"{s['title']}\nUpdated: {s['updated_at'][:16]}")
            self.session_list.addItem(item)
            if s["id"] == self.current_session_id:
                item.setSelected(True)
        self.session_list.blockSignals(False)

    def on_session_selected(self, item: QtWidgets.QListWidgetItem):
        sid = item.data(Qt.ItemDataRole.UserRole)
        if sid and sid != self.current_session_id:
            self.current_session_id = sid
            self.load_session_messages(sid)

    def load_session_messages(self, session_id: str):
        self.clear_chat_widgets()
        self.conversation_history.clear()
        session_info = self.db.get_session(session_id)
        if session_info:
            p_name = session_info.get("persona", DEFAULT_PERSONA)
            idx = self.persona_combo.findText(p_name)
            if idx >= 0:
                self.persona_combo.setCurrentIndex(idx)
        
        messages = self.db.get_messages(session_id)
        if not messages:
            self.add_welcome_message()
            return
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            m_used = msg.get("model", "")
            self.conversation_history.append({"role": role, "content": content})
            bubble = ChatBubble(role, content, m_used)
            self.messages_layout.insertWidget(self.messages_layout.count() - 1, bubble)
        self.scroll_to_bottom()

    def clear_chat_widgets(self):
        while self.messages_layout.count() > 1:
            item = self.messages_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def delete_current_session(self):
        if not self.current_session_id:
            return
        reply = QtWidgets.QMessageBox.question(
            self,
            "Delete Conversation",
            "Are you sure you want to delete this conversation from the database?",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.db.delete_session(self.current_session_id)
            self.load_or_create_session()

    def send_message(self):
        text = self.prompt_input.toPlainText().strip()
        if not text:
            return

        selected_model = self.model_combo.currentText()
        if not selected_model:
            selected_model = self.config.default_model

        if not self.current_session_id:
            self.create_new_session()

        # Update title if it's the first message of a new session
        session_info = self.db.get_session(self.current_session_id)
        if session_info and session_info["title"] == "New Conversation":
            short_title = text.strip().replace("\n", " ")[:26]
            self.db.update_session_title(self.current_session_id, short_title)
            self.refresh_session_list()

        # Save user message to database
        self.db.add_message(self.current_session_id, "user", text, model=selected_model)

        # Add user message to UI
        user_bubble = ChatBubble("user", text)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, user_bubble)
        self.prompt_input.clear()
        self.scroll_to_bottom()

        # Add assistant response bubble placeholder
        current_persona = self.persona_combo.currentText()
        assistant_bubble = ChatBubble("assistant", "Synthesizing neural response...", current_persona)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, assistant_bubble)
        self.current_bubble = assistant_bubble

        # Prepare messages array with System Persona
        system_content = PERSONAS.get(current_persona, {}).get("system_prompt", "")
        api_messages = [{"role": "system", "content": f"You are Afnan's AI. {system_content}"}]
        
        # Add past history from database
        recent_db_msgs = self.db.get_messages(self.current_session_id)
        for msg in recent_db_msgs[-7:]:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        # Context limit and parameters
        ctx_map = {0: 1024, 1: 2048, 2: 4096}
        num_ctx = ctx_map.get(self.ctx_combo.currentIndex(), 2048)
        temperature = self.temp_slider.value() / 10.0
        
        # GPU Layers: 0 if CPU Mode, 99 if GPU Mode
        gpu_layers = 0 if self.is_cpu_mode else 99

        # UI state for streaming
        self.send_btn.setVisible(False)
        self.stop_btn.setVisible(True)

        # Launch streaming worker thread
        self.current_worker = ChatWorker(
            client=self.client,
            messages=api_messages,
            model=selected_model,
            temperature=temperature,
            num_ctx=num_ctx,
            gpu_layers=gpu_layers
        )
        self.current_worker.token_received.connect(self.on_token_received)
        self.current_worker.finished_stream.connect(lambda full: self.on_stream_finished(text, full))
        self.current_worker.error_occurred.connect(self.on_stream_error)
        self.current_worker.start()

    def on_token_received(self, token: str):
        if self.current_bubble and self.current_worker:
            self.current_bubble.update_text(self.current_worker.full_response)
            self.scroll_to_bottom()

    def on_stream_finished(self, user_text: str, full_response: str):
        self.conversation_history.append({"role": "user", "content": user_text})
        self.conversation_history.append({"role": "assistant", "content": full_response})
        
        # Persist assistant response to SQLite database
        selected_model = self.model_combo.currentText() or self.config.default_model
        if self.current_session_id:
            self.db.add_message(
                self.current_session_id,
                "assistant",
                full_response,
                model=selected_model
            )
            self.refresh_session_list()

        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)
        self.scroll_to_bottom()

    def on_stream_error(self, err_msg: str):
        if self.current_bubble:
            self.current_bubble.update_text(f"⚠️ Neural Link Exception: {err_msg}")
        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)

    def stop_generation(self):
        if self.client:
            self.client.stop_generation()
        self.send_btn.setVisible(True)
        self.stop_btn.setVisible(False)

    def scroll_to_bottom(self):
        QtCore.QTimer.singleShot(50, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

    def export_chat(self):
        if not self.current_session_id:
            QtWidgets.QMessageBox.information(self, "Export", "No active conversation to export.")
            return

        messages = self.db.get_messages(self.current_session_id)
        if not messages:
            QtWidgets.QMessageBox.information(self, "Export", "No messages in this conversation.")
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save Conversation", "Afnan_AI_Chat.md", "Markdown (*.md);;JSON (*.json)"
        )
        if not file_path:
            return

        try:
            if file_path.endswith(".json"):
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(messages, f, indent=2)
            else:
                md_content = self.db.export_session_markdown(self.current_session_id)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
            QtWidgets.QMessageBox.information(self, "Export", f"Conversation saved to:\n{file_path}")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Export Error", f"Failed to save file: {e}")

    def closeEvent(self, event):
        """Clean up background workers on close."""
        if self.current_worker and self.current_worker.isRunning():
            self.client.stop_generation()
            self.current_worker.wait(500)
        event.accept()

def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
