from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from PySide6.QtGui import QColor


@dataclass(frozen=True)
class ModeTheme:
    name: str
    accent: str
    glow: str


MODE_THEMES: Dict[str, ModeTheme] = {
    "PASSIVE": ModeTheme("PASSIVE", "#10B981", "rgba(16, 185, 129, 0.34)"),
    "ASSISTED": ModeTheme("ASSISTED", "#F59E0B", "rgba(245, 158, 11, 0.34)"),
    "ACTIVE": ModeTheme("ACTIVE", "#EF4444", "rgba(239, 68, 68, 0.40)"),
}

BASE_BG = "#121212"
SURFACE_BG = "rgba(30, 30, 30, 0.76)"
TEXT_PRIMARY = "#F5F5F5"
TEXT_SECONDARY = "#A1A1AA"
BORDER = "rgba(255, 255, 255, 0.08)"


def color_lerp(start_hex: str, end_hex: str, progress: float) -> str:
    s = QColor(start_hex)
    e = QColor(end_hex)
    r = int(s.red() + (e.red() - s.red()) * progress)
    g = int(s.green() + (e.green() - s.green()) * progress)
    b = int(s.blue() + (e.blue() - s.blue()) * progress)
    return f"#{r:02X}{g:02X}{b:02X}"


def build_stylesheet(accent_hex: str) -> str:
    return f"""
        QWidget {{
            color: {TEXT_PRIMARY};
            font-family: 'Segoe UI Variable', 'Inter', 'Segoe UI', sans-serif;
            font-size: 13px;
        }}
        #rootPanel {{
            background: {SURFACE_BG};
            border: 1px solid {BORDER};
            border-radius: 14px;
        }}
        #topBar {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            min-height: 34px;
        }}
        #chatList, #logsView {{
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid {BORDER};
            border-radius: 12px;
            padding: 6px;
        }}
        #inputBox {{
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid {BORDER};
            border-radius: 10px;
            padding: 8px;
        }}
        QPushButton#sendButton {{
            background: {accent_hex};
            border-radius: 10px;
            color: white;
            padding: 8px 14px;
            font-weight: 600;
        }}
        QPushButton#killButton {{
            background: qradialgradient(cx:0.5, cy:0.5, radius:1.0, fx:0.5, fy:0.5,
                stop:0 {accent_hex}, stop:1 #6B0B0B);
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 12px;
            color: white;
            font-weight: 700;
            padding: 10px;
        }}
        QComboBox#modeSwitcher {{
            background: rgba(255, 255, 255, 0.06);
            border: 1px solid {BORDER};
            border-radius: 9px;
            padding: 7px;
        }}
        #connectionLabel {{ color: {TEXT_SECONDARY}; }}
    """
