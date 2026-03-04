from __future__ import annotations

import queue
import signal
import threading
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

from aia.agent.executor import ActionExecutor
from aia.agent.ipc_server import IPCServer
from aia.agent.logger import JsonAuditLogger
from aia.agent.planner import GeminiPlanner
from aia.agent.security import classify_step
from aia.agent.voice import VoiceListener
from aia.shared.message_protocol import Message, MessageType, Mode, build_message


class AgentCore:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        self.mode = Mode.PASSIVE
        self.executor = ActionExecutor()
        self.logger = JsonAuditLogger(Path("logs/aia_audit.jsonl"))
        self.planner = GeminiPlanner()
        self.task_queue: queue.Queue[str] = queue.Queue()
        self.pending_confirmations: dict[str, queue.Queue[bool]] = {}
        self.kill_event = threading.Event()

        self.ipc_server = IPCServer(host, port, self._handle_message)
        self.voice_listener = VoiceListener(model_path=None, on_command=self.enqueue_task)

    def start(self) -> None:
        self.ipc_server.start()
        self.voice_listener.start()
        threading.Thread(target=self._task_loop, daemon=True).start()
        self._emit_log("agent_started", {})

    def stop(self) -> None:
        self.voice_listener.stop()
        self.ipc_server.stop()

    def enqueue_task(self, command: str) -> None:
        self.task_queue.put(command)
        self._emit_log("new_task", {"command": command})

    def _handle_message(self, message: Message, _client) -> None:
        if message.message_type == MessageType.NEW_TASK:
            cmd = str(message.payload.get("command", "")).strip()
            if cmd:
                self.enqueue_task(cmd)
        elif message.message_type == MessageType.MODE_CHANGE:
            self.mode = Mode(message.payload["mode"])
            self._emit_status()
        elif message.message_type == MessageType.KILL_SIGNAL:
            self._kill_switch("ipc")
        elif message.message_type == MessageType.CONFIRMATION_RESPONSE and message.request_id:
            decision = bool(message.payload.get("approved", False))
            pending = self.pending_confirmations.get(message.request_id)
            if pending:
                pending.put(decision)

    def _task_loop(self) -> None:
        while True:
            command = self.task_queue.get()
            self.kill_event.clear()
            self.executor.reset()
            try:
                plan = self.planner.build_plan(command)
                secured_plan = [classify_step(step) for step in plan]
                self.ipc_server.broadcast(build_message(MessageType.PLAN_RESULT, {"command": command, "plan": secured_plan}))
                self._emit_log("plan_result", {"command": command, "plan": secured_plan})

                if self.mode == Mode.PASSIVE:
                    continue

                for step in secured_plan:
                    if self.kill_event.is_set():
                        break
                    if not self._is_step_allowed(step):
                        self._emit_log("step_skipped", {"step": step, "reason": "not_approved"})
                        continue
                    result = self.executor.execute(step)
                    self.ipc_server.broadcast(build_message(MessageType.EXECUTE_STEP, {"step": step, "result": result}))
                    self._emit_log("step_executed", {"step": step, "result": result})
            except Exception as exc:  # noqa: BLE001
                self._emit_log("error", {"error": str(exc), "command": command})

    def _is_step_allowed(self, step: Dict[str, Any]) -> bool:
        if self.mode == Mode.ASSISTED:
            return self._request_confirmation(step)
        if self.mode == Mode.ACTIVE and step.get("is_critical"):
            return self._request_confirmation(step)
        return self.mode == Mode.ACTIVE

    def _request_confirmation(self, step: Dict[str, Any]) -> bool:
        request_id = str(uuid.uuid4())
        result_queue: queue.Queue[bool] = queue.Queue(maxsize=1)
        self.pending_confirmations[request_id] = result_queue
        self.ipc_server.broadcast(build_message(MessageType.REQUEST_CONFIRMATION, {"step": step}, request_id=request_id))

        try:
            decision = result_queue.get(timeout=120)
            self._emit_log("confirmation_decision", {"step": step, "approved": decision})
            return decision
        except queue.Empty:
            self._emit_log("confirmation_timeout", {"step": step})
            return False
        finally:
            self.pending_confirmations.pop(request_id, None)

    def _kill_switch(self, source: str) -> None:
        self.kill_event.set()
        with self.task_queue.mutex:
            self.task_queue.queue.clear()
        self.executor.stop()
        self.mode = Mode.PASSIVE
        self._emit_log("kill_switch", {"source": source})
        self._emit_status()

    def _emit_log(self, event_type: str, details: Dict[str, Any]) -> None:
        self.logger.log_event(event_type, self.mode.value, details)
        self.ipc_server.broadcast(build_message(MessageType.LOG_UPDATE, {"event_type": event_type, "details": details}))

    def _emit_status(self) -> None:
        self.ipc_server.broadcast(build_message(MessageType.STATUS_UPDATE, {"mode": self.mode.value}))


def run_agent() -> None:
    agent = AgentCore()
    agent.start()

    def handle_signal(_sig, _frame) -> None:
        agent.stop()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    threading.Event().wait()


if __name__ == "__main__":
    run_agent()
