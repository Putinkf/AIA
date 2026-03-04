from __future__ import annotations

import json
import socket
import threading
from typing import Callable, Optional

from aia.shared.message_protocol import Message


class IPCClient:
    def __init__(
        self,
        host: str,
        port: int,
        on_message: Callable[[Message], None],
        on_connection_changed: Optional[Callable[[bool], None]] = None,
    ) -> None:
        self.host = host
        self.port = port
        self.on_message = on_message
        self.on_connection_changed = on_connection_changed
        self.sock: Optional[socket.socket] = None
        self._running = threading.Event()
        self._send_lock = threading.Lock()
        self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self.sock is not None

    def connect(self, timeout_s: float = 2.0) -> bool:
        self.disconnect()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout_s)
        try:
            sock.connect((self.host, self.port))
        except OSError:
            sock.close()
            self._set_connected(False)
            return False

        sock.settimeout(None)
        self.sock = sock
        self._running.set()
        self._set_connected(True)
        threading.Thread(target=self._reader_loop, daemon=True).start()
        return True

    def disconnect(self) -> None:
        self._running.clear()
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.sock.close()
            self.sock = None
        self._set_connected(False)

    def send(self, message: Message) -> bool:
        if not self.sock or not self._connected:
            return False

        payload = (message.to_json() + "\n").encode("utf-8")
        with self._send_lock:
            if not self.sock or not self._connected:
                return False
            try:
                self.sock.sendall(payload)
                return True
            except OSError:
                self.disconnect()
                return False

    def _reader_loop(self) -> None:
        buffer = ""
        while self._running.is_set():
            sock = self.sock
            if sock is None:
                break
            try:
                chunk = sock.recv(4096)
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
        self.disconnect()

    def _set_connected(self, value: bool) -> None:
        changed = self._connected != value
        self._connected = value
        if changed and self.on_connection_changed:
            self.on_connection_changed(value)
