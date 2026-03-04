from __future__ import annotations

import json
import socket
import threading
from typing import Callable, Optional

from aia.shared.message_protocol import Message


class IPCClient:
    def __init__(self, host: str, port: int, on_message: Callable[[Message], None]) -> None:
        self.host = host
        self.port = port
        self.on_message = on_message
        self.sock: Optional[socket.socket] = None
        self._running = threading.Event()

    def connect(self) -> None:
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self._running.set()
        threading.Thread(target=self._reader_loop, daemon=True).start()

    def disconnect(self) -> None:
        self._running.clear()
        if self.sock:
            self.sock.close()
            self.sock = None

    def send(self, message: Message) -> None:
        if not self.sock:
            raise RuntimeError("IPC client is disconnected")
        self.sock.sendall((message.to_json() + "\n").encode("utf-8"))

    def _reader_loop(self) -> None:
        assert self.sock is not None
        buffer = ""
        while self._running.is_set():
            try:
                chunk = self.sock.recv(4096)
            except OSError:
                break
            if not chunk:
                break
            buffer += chunk.decode("utf-8")
            while "\n" in buffer:
                raw, buffer = buffer.split("\n", 1)
                if not raw.strip():
                    continue
                try:
                    message = Message.from_json(raw)
                except (ValueError, json.JSONDecodeError):
                    continue
                self.on_message(message)
