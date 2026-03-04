from __future__ import annotations

from pathlib import PureWindowsPath
from typing import Any, Dict, List

CRITICAL_ACTIONS = {"delete_file", "move_file", "download_file", "type_text", "batch_action"}
SENSITIVE_PATH_PREFIXES = [
    PureWindowsPath("C:/Windows"),
    PureWindowsPath("C:/Program Files"),
    PureWindowsPath("C:/Program Files (x86)"),
]
BANKING_KEYWORDS = {"bank", "payment", "swift", "visa", "mastercard", "secure-login"}
PASSWORD_KEYWORDS = {"password", "pass", "пароль", "otp", "2fa"}


def _looks_sensitive_path(path_value: str) -> bool:
    windows_path = PureWindowsPath(path_value)
    return any(str(windows_path).lower().startswith(str(prefix).lower()) for prefix in SENSITIVE_PATH_PREFIXES)


def _contains_keywords(raw: str, keywords: set[str]) -> bool:
    raw_low = raw.lower()
    return any(word in raw_low for word in keywords)


def classify_step(step: Dict[str, Any]) -> Dict[str, Any]:
    reasons: List[str] = []
    action_type = str(step.get("action_type", ""))
    params = step.get("parameters", {})

    if action_type in {"delete_file", "move_file"}:
        reasons.append("filesystem_modification")

    if action_type == "download_file" and str(params.get("url", "")).lower().endswith(".exe"):
        reasons.append("executable_download")

    if action_type == "batch_action" and int(params.get("repeat", 0)) > 10:
        reasons.append("mass_repeated_action")

    path_value = str(params.get("path") or params.get("target_path") or "")
    if path_value and _looks_sensitive_path(path_value):
        reasons.append("system_directory_access")

    text_value = str(params.get("text", ""))
    field_hint = str(params.get("field_hint", ""))
    if action_type == "type_text" and (_contains_keywords(field_hint, PASSWORD_KEYWORDS) or _contains_keywords(text_value, PASSWORD_KEYWORDS)):
        reasons.append("password_like_field")

    target = str(params.get("target") or params.get("url") or "")
    if _contains_keywords(target, BANKING_KEYWORDS):
        reasons.append("banking_related_domain")

    explicit_critical = bool(step.get("is_critical"))
    if explicit_critical:
        reasons.append("planner_marked_critical")

    return {
        **step,
        "is_critical": bool(reasons) or explicit_critical or action_type in CRITICAL_ACTIONS,
        "critical_reasons": reasons,
    }
