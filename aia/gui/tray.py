from __future__ import annotations

import threading
from typing import Callable, Dict

try:
    import pystray
    from PIL import Image, ImageDraw
except ImportError:  # optional runtime dependency
    pystray = None
    Image = None
    ImageDraw = None


MODE_COLORS: Dict[str, str] = {
    "PASSIVE": "#10B981",
    "ASSISTED": "#F59E0B",
    "ACTIVE": "#EF4444",
}


class TrayController:
    def __init__(self, on_open: Callable[[], None], on_mode: Callable[[str], None], on_kill: Callable[[], None], on_exit: Callable[[], None]) -> None:
        self.on_open = on_open
        self.on_mode = on_mode
        self.on_kill = on_kill
        self.on_exit = on_exit
        self.icon = None

    def start(self, mode: str = "PASSIVE") -> None:
        if pystray is None:
            return
        image = self._make_icon(MODE_COLORS.get(mode, "#10B981"))
        menu = pystray.Menu(
            pystray.MenuItem("Open", lambda icon, item: self.on_open()),
            pystray.MenuItem("Passive", lambda icon, item: self.on_mode("PASSIVE")),
            pystray.MenuItem("Assisted", lambda icon, item: self.on_mode("ASSISTED")),
            pystray.MenuItem("Active", lambda icon, item: self.on_mode("ACTIVE")),
            pystray.MenuItem("Kill Switch", lambda icon, item: self.on_kill()),
            pystray.MenuItem("Exit", lambda icon, item: self.on_exit()),
        )
        self.icon = pystray.Icon("AIA", image, "AIA Agent", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def update_mode(self, mode: str) -> None:
        if self.icon is None:
            return
        self.icon.icon = self._make_icon(MODE_COLORS.get(mode, "#10B981"))
        self.icon.title = f"AIA ({mode})"

    def stop(self) -> None:
        if self.icon:
            self.icon.stop()

    def _make_icon(self, color: str):
        if Image is None or ImageDraw is None:
            return None
        image = Image.new("RGB", (64, 64), color="#0B0B0B")
        draw = ImageDraw.Draw(image)
        draw.ellipse((8, 8, 56, 56), fill=color)
        return image
