from __future__ import annotations

import time
import webbrowser
from pathlib import Path
from typing import Any, Dict

try:
    import pyautogui
except ImportError:  # optional runtime dependency
    pyautogui = None

try:
    import win32gui
except ImportError:  # optional runtime dependency
    win32gui = None


class ActionExecutor:
    def __init__(self) -> None:
        self._stop_requested = False

    def stop(self) -> None:
        self._stop_requested = True

    def reset(self) -> None:
        self._stop_requested = False

    def execute(self, step: Dict[str, Any]) -> Dict[str, Any]:
        if self._stop_requested:
            return {"ok": False, "error": "execution_stopped"}

        action_type = step.get("action_type")
        params = step.get("parameters", {})
        handler = getattr(self, f"_do_{action_type}", None)
        if handler is None:
            return {"ok": False, "error": f"unknown_action:{action_type}"}
        return handler(params)

    def _do_open_application(self, params: Dict[str, Any]) -> Dict[str, Any]:
        path = params.get("path")
        if not path:
            return {"ok": False, "error": "missing_path"}
        Path(path).expanduser()
        __import__("os").startfile(path)
        return {"ok": True}

    def _do_click(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if pyautogui is None:
            return {"ok": False, "error": "pyautogui_not_installed"}
        pyautogui.click(x=int(params.get("x", 0)), y=int(params.get("y", 0)), button=params.get("button", "left"))
        return {"ok": True}

    def _do_type_text(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if pyautogui is None:
            return {"ok": False, "error": "pyautogui_not_installed"}
        pyautogui.write(str(params.get("text", "")), interval=float(params.get("interval", 0.02)))
        return {"ok": True}

    def _do_press_key(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if pyautogui is None:
            return {"ok": False, "error": "pyautogui_not_installed"}
        pyautogui.press(str(params.get("key", "enter")))
        return {"ok": True}

    def _do_wait(self, params: Dict[str, Any]) -> Dict[str, Any]:
        time.sleep(float(params.get("seconds", 1)))
        return {"ok": True}

    def _do_search_browser(self, params: Dict[str, Any]) -> Dict[str, Any]:
        query = str(params.get("query", "")).strip()
        if not query:
            return {"ok": False, "error": "missing_query"}
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return {"ok": True}

    def _do_save_file(self, params: Dict[str, Any]) -> Dict[str, Any]:
        content = str(params.get("content", ""))
        path = Path(str(params.get("path", "output.txt"))).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return {"ok": True, "path": str(path)}

    def _do_focus_window(self, params: Dict[str, Any]) -> Dict[str, Any]:
        if win32gui is None:
            return {"ok": False, "error": "pywin32_not_installed"}
        title = str(params.get("title", ""))
        hwnd = win32gui.FindWindow(None, title)
        if not hwnd:
            return {"ok": False, "error": f"window_not_found:{title}"}
        win32gui.SetForegroundWindow(hwnd)
        return {"ok": True}
