from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)


class ConfirmationDialog(QDialog):
    def __init__(self, title: str, details: str, timeout_sec: int = 20, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
        self.setModal(True)
        self.resize(520, 340)

        self.setStyleSheet(
            """
            QDialog { background: rgba(26,26,26,0.92); border: 1px solid rgba(255,255,255,0.18); border-radius: 14px; }
            QLabel#warningIcon { color: #F59E0B; font-size: 24px; }
            QPushButton#allowBtn { background: #EF4444; color: white; font-weight: 700; border-radius: 10px; padding: 10px; }
            QPushButton#denyBtn { background: transparent; color: white; border: 1px solid rgba(255,255,255,0.28); border-radius: 10px; padding: 10px; }
            QTextEdit { background: rgba(255,255,255,0.03); border-radius: 10px; border: 1px solid rgba(255,255,255,0.09); }
            QProgressBar { border: none; background: rgba(255,255,255,0.08); height: 5px; border-radius: 2px; }
            QProgressBar::chunk { background: #F59E0B; border-radius: 2px; }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)

        self.progress = QProgressBar()
        self.progress.setRange(0, max(timeout_sec, 1))
        self.progress.setValue(timeout_sec)
        layout.addWidget(self.progress)

        title_row = QHBoxLayout()
        warning = QLabel("⚠")
        warning.setObjectName("warningIcon")
        title_row.addWidget(warning)
        title_row.addWidget(QLabel("Требуется подтверждение критического действия"))
        title_row.addStretch(1)
        layout.addLayout(title_row)

        body = QTextEdit()
        body.setReadOnly(True)
        body.setText(details)
        layout.addWidget(body, 1)

        buttons = QHBoxLayout()
        self.allow_btn = QPushButton("ALLOW EXECUTION")
        self.allow_btn.setObjectName("allowBtn")
        self.deny_btn = QPushButton("DENY")
        self.deny_btn.setObjectName("denyBtn")
        self.allow_btn.clicked.connect(self.accept)
        self.deny_btn.clicked.connect(self.reject)
        buttons.addWidget(self.deny_btn)
        buttons.addWidget(self.allow_btn)
        layout.addLayout(buttons)

        self._remaining = timeout_sec
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def showEvent(self, event) -> None:  # type: ignore[override]
        super().showEvent(event)
        start_pos = self.pos()
        start_pos.setY(start_pos.y() - 60)
        self.move(start_pos)
        self._slide = QPropertyAnimation(self, b"pos", self)
        self._slide.setDuration(260)
        self._slide.setStartValue(start_pos)
        end_pos = self.pos()
        end_pos.setY(end_pos.y() + 60)
        self._slide.setEndValue(end_pos)
        self._slide.setEasingCurve(QEasingCurve.OutCubic)
        self._slide.start()

    def _tick(self) -> None:
        self._remaining -= 1
        self.progress.setValue(max(self._remaining, 0))
        if self._remaining <= 0:
            self.reject()
