from __future__ import annotations

import random

from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class VoiceVisualizer(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(58)
        self._bars = [0.2] * 28
        self._accent = QColor("#10B981")
        self._listening = True
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(70)

    def set_accent(self, accent_hex: str) -> None:
        self._accent = QColor(accent_hex)
        self.update()

    def set_listening(self, listening: bool) -> None:
        self._listening = listening

    def _tick(self) -> None:
        if self._listening:
            self._bars = [random.uniform(0.1, 1.0) for _ in self._bars]
        else:
            self._bars = [max(b * 0.75, 0.1) for b in self._bars]
        self.update()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), Qt.transparent)

        center_y = self.height() // 2
        width_step = max(self.width() // max(len(self._bars), 1), 6)
        for i, amp in enumerate(self._bars):
            x = 8 + i * width_step
            h = int(amp * 22)
            c = QColor(self._accent)
            c.setAlpha(180)
            painter.setPen(QPen(c, 3, Qt.SolidLine, Qt.RoundCap))
            painter.drawLine(x, center_y - h, x, center_y + h)


class ChatWidget(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.root_panel = QFrame()
        self.root_panel.setObjectName("rootPanel")

        self.top_bar = QFrame()
        self.top_bar.setObjectName("topBar")
        self.connection_dot = QLabel("●")
        self.connection_dot.setStyleSheet("color:#10B981; font-size: 14px;")
        self.connection_label = QLabel("Agent Process: Offline")
        self.connection_label.setObjectName("connectionLabel")
        self.mode_switcher = QComboBox()
        self.mode_switcher.setObjectName("modeSwitcher")
        self.mode_switcher.addItems(["PASSIVE", "ASSISTED", "ACTIVE"])
        self.collapse_button = QPushButton("◧")
        self.collapse_button.setToolTip("Pill/Panel")

        top_row = QHBoxLayout(self.top_bar)
        top_row.setContentsMargins(12, 4, 12, 4)
        top_row.addWidget(self.connection_dot)
        top_row.addWidget(self.connection_label)
        top_row.addStretch(1)
        top_row.addWidget(self.mode_switcher)
        top_row.addWidget(self.collapse_button)

        self.chat_history = QListWidget()
        self.chat_history.setObjectName("chatList")

        self.logs = QTextEdit()
        self.logs.setObjectName("logsView")
        self.logs.setReadOnly(True)
        self.logs.setFixedHeight(120)

        self.input_box = QLineEdit()
        self.input_box.setObjectName("inputBox")
        self.input_box.setPlaceholderText("Скажите или введите команду...")
        self.send_button = QPushButton("Отправить")
        self.send_button.setObjectName("sendButton")

        input_row = QHBoxLayout()
        input_row.addWidget(self.input_box, 1)
        input_row.addWidget(self.send_button)

        self.voice_visualizer = VoiceVisualizer()

        self.kill_button = QPushButton("EMERGENCY STOP  Ctrl+Alt+X")
        self.kill_button.setObjectName("killButton")

        panel_layout = QVBoxLayout(self.root_panel)
        panel_layout.setContentsMargins(12, 12, 12, 12)
        panel_layout.addWidget(self.top_bar)
        panel_layout.addWidget(self.chat_history, 1)
        panel_layout.addLayout(input_row)
        panel_layout.addWidget(self.logs)
        panel_layout.addWidget(self.voice_visualizer)
        panel_layout.addWidget(self.kill_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.root_panel)

    def set_connection(self, online: bool) -> None:
        if online:
            self.connection_dot.setStyleSheet("color:#10B981; font-size: 14px;")
            self.connection_label.setText("Agent Process: Online")
        else:
            self.connection_dot.setStyleSheet("color:#EF4444; font-size: 14px;")
            self.connection_label.setText("Agent Process: Offline")

    def append_user_message(self, text: str) -> None:
        self.chat_history.addItem(f"🧑 {text}")
        self.chat_history.scrollToBottom()

    def append_agent_message(self, text: str) -> None:
        self.chat_history.addItem(f"🤖 {text}")
        self.chat_history.scrollToBottom()
