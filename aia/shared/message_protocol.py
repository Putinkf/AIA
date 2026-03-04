from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class MessageType(str, Enum):
    NEW_TASK = "NEW_TASK"
    PLAN_RESULT = "PLAN_RESULT"
    EXECUTE_STEP = "EXECUTE_STEP"
    REQUEST_CONFIRMATION = "REQUEST_CONFIRMATION"
    CONFIRMATION_RESPONSE = "CONFIRMATION_RESPONSE"
    MODE_CHANGE = "MODE_CHANGE"
    KILL_SIGNAL = "KILL_SIGNAL"
    LOG_UPDATE = "LOG_UPDATE"
    STATUS_UPDATE = "STATUS_UPDATE"
    GUI_COMMAND = "GUI_COMMAND"


class Mode(str, Enum):
    PASSIVE = "PASSIVE"
    ASSISTED = "ASSISTED"
    ACTIVE = "ACTIVE"


@dataclass(slots=True)
class Message:
    message_type: MessageType
    payload: Dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(tz=timezone.utc).isoformat())

    def to_json(self) -> str:
        body = {
            "message_type": self.message_type.value,
            "payload": self.payload,
            "request_id": self.request_id,
            "timestamp": self.timestamp,
        }
        return json.dumps(body, ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> "Message":
        obj = json.loads(raw)
        return cls(
            message_type=MessageType(obj["message_type"]),
            payload=obj.get("payload", {}),
            request_id=obj.get("request_id"),
            timestamp=obj.get("timestamp") or datetime.now(tz=timezone.utc).isoformat(),
        )


def build_message(message_type: MessageType, payload: Optional[Dict[str, Any]] = None, request_id: Optional[str] = None) -> Message:
    return Message(message_type=message_type, payload=payload or {}, request_id=request_id)
