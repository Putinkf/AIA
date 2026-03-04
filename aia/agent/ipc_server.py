from __future__ import annotations

import json
import socket
import threading
from typing import Callable, Optional

from aia.shared.message_protocol import Message


class IPCServer:
    def __init__(self, host: str, port: int, on_message: Callable[[Message, socket.socket], None]) -> None:
        self.host = host
        self.port = port
        self.on_message = on_message
        self._server: Optional[socket.socket] = None
        self._running = threading.Event()
        self._clients: list[socket.socket] = []
        self._lock = threading.Lock()

    def start(self) -> None:
        self._running.set()
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self.host, self.port))
        self._server.listen(5)
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def stop(self) -> None:
        self._running.clear()
        if self._server:
            self._server.close()
        with self._lock:
            for client in self._clients:
                client.close()
            self._clients.clear()

    def broadcast(self, message: Message) -> None:
        data = (message.to_json() + "\n").encode("utf-8")
        with self._lock:
            dead = []
            for client in self._clients:
                try:
                    client.sendall(data)
                except OSError:
                    dead.append(client)
            for item in dead:
                self._clients.remove(item)

    def _accept_loop(self) -> None:
        assert self._server is not None
        while self._running.is_set():
            try:
                client, _ = self._server.accept()
            except OSError:
                break
            with self._lock:
                self._clients.append(client)
            threading.Thread(target=self._client_loop, args=(client,), daemon=True).start()

    def _client_loop(self, client: socket.socket) -> None:
        buffer = ""
        while self._running.is_set():
            try:
                chunk = client.recv(4096)
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
                    msg = Message.from_json(raw)
                except (json.JSONDecodeError, ValueError):
                    continue
                self.on_message(msg, client)
        with self._lock:
            if client in self._clients:
                self._clients.remove(client)
        client.close()
