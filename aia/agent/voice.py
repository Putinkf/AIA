from __future__ import annotations

import json
import queue
import threading
from typing import Callable, Optional

try:
    import sounddevice as sd
    from vosk import KaldiRecognizer, Model
except ImportError:  # optional runtime dependency
    sd = None
    Model = None
    KaldiRecognizer = None


class VoiceListener:
    def __init__(self, model_path: Optional[str], on_command: Callable[[str], None]) -> None:
        self.model_path = model_path
        self.on_command = on_command
        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._fallback_queue: queue.Queue[str] = queue.Queue()

    def push_text_fallback(self, text: str) -> None:
        self._fallback_queue.put(text)

    def start(self) -> None:
        self._running.set()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1)

    def _run_loop(self) -> None:
        if Model and sd and self.model_path:
            self._run_vosk()
        else:
            self._run_fallback_loop()

    def _run_fallback_loop(self) -> None:
        while self._running.is_set():
            try:
                text = self._fallback_queue.get(timeout=0.3)
            except queue.Empty:
                continue
            if text.strip():
                self.on_command(text.strip())

    def _run_vosk(self) -> None:
        model = Model(self.model_path)
        recognizer = KaldiRecognizer(model, 16000)

        def callback(indata, frames, time, status) -> None:  # type: ignore[no-untyped-def]
            if status:
                return
            if recognizer.AcceptWaveform(bytes(indata)):
                raw = recognizer.Result()
                parsed = json.loads(raw)
                text = parsed.get("text", "").strip()
                if text:
                    self.on_command(text)

        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype="int16", channels=1, callback=callback):
            while self._running.is_set():
                sd.sleep(200)
