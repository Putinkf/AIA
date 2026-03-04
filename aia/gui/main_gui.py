from __future__ import annotations

import json
import sys

from PySide6.QtCore import QEvent, QEasingCurve, QObject, QPoint, QPropertyAnimation, QRect, Qt, QTimer, Signal, QVariantAnimation
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QMainWindow, QWidget

from aia.gui.chat_widget import ChatWidget
from aia.gui.confirmation_dialog import ConfirmationDialog
from aia.gui.design_system import MODE_THEMES, build_stylesheet, color_lerp
from aia.gui.ipc_client import IPCClient
from aia.gui.tray import TrayController
from aia.shared.message_protocol import Message, MessageType, build_message

try:
    import keyboard
except ImportError:  # optional runtime dependency
    keyboard = None


class EventBus(QObject):
    message = Signal(object)


class FlashOverlay(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)
        self.setStyleSheet("background: rgba(239,68,68,0.0); border-radius: 14px;")
        self.hide()

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        if self.parentWidget():
            self.setGeometry(self.parentWidget().rect())

    def flash(self) -> None:
        self.setGeometry(self.parentWidget().rect())
        self.show()
        anim = QVariantAnimation(self)
        anim.setDuration(280)
        anim.setStartValue(0.32)
        anim.setEndValue(0.0)
        anim.valueChanged.connect(lambda v: self.setStyleSheet(f"background: rgba(239,68,68,{float(v):.3f}); border-radius: 14px;"))
        anim.finished.connect(self.hide)
        anim.start()
        self._anim = anim


class MainWindow(QMainWindow):
    PANEL_SIZE = (420, 640)
    PILL_SIZE = (260, 88)

    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        super().__init__()
        self._mode = "PASSIVE"
        self._is_pill = False
        self._drag_offset = QPoint()

        self.setWindowTitle("AIA Desktop Assistant")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.widget = ChatWidget()
        self.setCentralWidget(self.widget)
        self.resize(*self.PANEL_SIZE)

        self.overlay = FlashOverlay(self.widget.root_panel)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(42)
        self.shadow.setOffset(0, 10)
        self.shadow.setColor(QColor(0, 0, 0, 185))
        self.widget.root_panel.setGraphicsEffect(self.shadow)

        self.bus = EventBus()
        self.bus.message.connect(self._process_message)

        self.ipc = IPCClient(
            host,
            port,
            on_message=lambda m: self.bus.message.emit(m),
            on_connection_changed=self.widget.set_connection,
        )
        self.widget.set_connection(False)
        self.ipc.connect()

        self.tray = TrayController(self.showNormal, self._change_mode, self._kill_switch, self._exit_app)
        self.tray.start(self._mode)

        self.widget.send_button.clicked.connect(self._send_command)
        self.widget.mode_switcher.currentTextChanged.connect(self._change_mode)
        self.widget.kill_button.clicked.connect(self._kill_switch)
        self.widget.collapse_button.clicked.connect(self._toggle_pill_mode)

        self.widget.top_bar.installEventFilter(self)

        self._breath_timer = QTimer(self)
        self._breath_timer.timeout.connect(self._pulse_glow)
        self._breath_phase = 0
        self._breath_timer.start(90)

        self._reconnect_timer = QTimer(self)
        self._reconnect_timer.timeout.connect(self._ensure_connected)
        self._reconnect_timer.start(2000)

        self._apply_mode_theme(self._mode, immediate=True)

        if keyboard is not None:
            keyboard.add_hotkey("ctrl+alt+x", self._kill_switch)

    def eventFilter(self, watched, event):  # type: ignore[override]
        if watched is self.widget.top_bar:
            if event.type() == QEvent.Type.MouseButtonPress and hasattr(event, "button") and event.button() == Qt.LeftButton:
                self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                return True
            if event.type() == QEvent.Type.MouseMove and hasattr(event, "buttons") and event.buttons() & Qt.LeftButton:
                self.move(event.globalPosition().toPoint() - self._drag_offset)
                return True
        return super().eventFilter(watched, event)

    def _send_command(self) -> None:
        text = self.widget.input_box.text().strip()
        if not text:
            return
        self.widget.append_user_message(text)
        self.widget.input_box.clear()
        self.widget.logs.append("⏳ Agent thinking...")
        self._send_ipc(build_message(MessageType.NEW_TASK, {"command": text}), "Не удалось отправить задачу: агент офлайн")

    def _change_mode(self, mode: str) -> None:
        if mode not in MODE_THEMES:
            return
        if mode != self._mode:
            self._apply_mode_theme(mode, immediate=False)
        self._send_ipc(build_message(MessageType.MODE_CHANGE, {"mode": mode}), "Не удалось сменить режим: агент офлайн")

    def _apply_mode_theme(self, mode: str, immediate: bool) -> None:
        old = self._mode
        self._mode = mode
        self.tray.update_mode(mode)
        self.widget.voice_visualizer.set_accent(MODE_THEMES[mode].accent)

        if immediate:
            self.setStyleSheet(build_stylesheet(MODE_THEMES[mode].accent))
            return

        anim = QVariantAnimation(self)
        anim.setDuration(300)
        anim.setEasingCurve(QEasingCurve.InOutCubic)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.valueChanged.connect(
            lambda p: self.setStyleSheet(
                build_stylesheet(color_lerp(MODE_THEMES[old].accent, MODE_THEMES[mode].accent, float(p)))
            )
        )
        anim.start()
        self._mode_anim = anim

    def _toggle_pill_mode(self) -> None:
        self._is_pill = not self._is_pill
        start = self.geometry()
        if self._is_pill:
            self.widget.chat_history.hide()
            self.widget.logs.hide()
            self.widget.input_box.hide()
            self.widget.send_button.hide()
            self.widget.kill_button.hide()
            target = QRect(self.x(), self.y(), *self.PILL_SIZE)
        else:
            self.widget.chat_history.show()
            self.widget.logs.show()
            self.widget.input_box.show()
            self.widget.send_button.show()
            self.widget.kill_button.show()
            target = QRect(self.x(), self.y(), *self.PANEL_SIZE)

        morph = QPropertyAnimation(self, b"geometry", self)
        morph.setDuration(420)
        morph.setStartValue(start)
        morph.setEndValue(target)
        morph.setEasingCurve(QEasingCurve.OutBack)
        morph.start()
        self._morph_anim = morph

    def _kill_switch(self) -> None:
        self.overlay.flash()
        self.widget.chat_history.clear()
        self.widget.logs.append("🛑 PANIC: execution stopped, switched to PASSIVE")
        self._apply_mode_theme("PASSIVE", immediate=False)
        if not self._is_pill:
            self._toggle_pill_mode()
        self._send_ipc(build_message(MessageType.KILL_SIGNAL, {"source": "gui"}), "Kill signal не отправлен: агент офлайн")

    def _pulse_glow(self) -> None:
        color = QColor(MODE_THEMES[self._mode].accent)
        self._breath_phase = (self._breath_phase + 1) % 60
        alpha = 90 + int(65 * abs(30 - self._breath_phase) / 30)
        self.shadow.setColor(QColor(color.red(), color.green(), color.blue(), alpha))

    def _process_message(self, message: Message) -> None:
        if message.message_type == MessageType.PLAN_RESULT:
            self.widget.append_agent_message(f"Plan generated: {json.dumps(message.payload, ensure_ascii=False)}")
        elif message.message_type == MessageType.EXECUTE_STEP:
            self.widget.logs.append(f"EXECUTE: {json.dumps(message.payload, ensure_ascii=False)}")
        elif message.message_type == MessageType.LOG_UPDATE:
            self.widget.logs.append(f"LOG: {json.dumps(message.payload, ensure_ascii=False)}")
        elif message.message_type == MessageType.STATUS_UPDATE:
            mode = message.payload.get("mode", "PASSIVE")
            idx = self.widget.mode_switcher.findText(mode)
            if idx >= 0:
                self.widget.mode_switcher.blockSignals(True)
                self.widget.mode_switcher.setCurrentIndex(idx)
                self.widget.mode_switcher.blockSignals(False)
            self._apply_mode_theme(mode, immediate=False)
        elif message.message_type == MessageType.REQUEST_CONFIRMATION:
            self._show_confirmation(message)

    def _show_confirmation(self, message: Message) -> None:
        step = message.payload.get("step", {})
        dlg = ConfirmationDialog(
            "Critical Action Confirmation",
            json.dumps(step, ensure_ascii=False, indent=2),
            timeout_sec=20,
            parent=self,
        )
        approved = dlg.exec() == ConfirmationDialog.Accepted
        self._send_ipc(
            build_message(
                MessageType.CONFIRMATION_RESPONSE,
                {"approved": approved},
                request_id=message.request_id,
            ),
            "Не удалось отправить подтверждение: агент офлайн",
        )

    def _ensure_connected(self) -> None:
        if not self.ipc.is_connected:
            self.ipc.connect()

    def _send_ipc(self, message: Message, offline_log: str) -> bool:
        ok = self.ipc.send(message)
        if not ok:
            self.widget.logs.append(f"⚠️ {offline_log}")
            self.widget.set_connection(False)
        return ok

    def _exit_app(self) -> None:
        self.tray.stop()
        self.ipc.disconnect()
        QApplication.quit()


def run_gui() -> None:
    app = QApplication(sys.argv)
    app_font: QFont = app.font()
    if app_font.pointSize() <= 0:
        app_font.setPointSize(10)
        app.setFont(app_font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run_gui()
