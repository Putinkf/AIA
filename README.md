# AIA (AI Agent Assistant) MVP

Windows-only desktop AI agent with **two-process architecture**:

1. **Background Agent (`aia/agent`)** — voice/text task intake, Gemini planning, security classification, execution, logging, IPC server.
2. **GUI Client (`aia/gui`)** — chat UX, mode switch, log stream, confirmation modal, tray control, kill switch.

IPC uses localhost TCP sockets (`127.0.0.1:8765`) with newline-delimited JSON messages from `aia/shared/message_protocol.py`.

## Project structure

```text
aia/
├── agent/
│   ├── main_agent.py
│   ├── planner.py
│   ├── executor.py
│   ├── security.py
│   ├── voice.py
│   ├── logger.py
│   └── ipc_server.py
├── gui/
│   ├── main_gui.py
│   ├── chat_widget.py
│   ├── tray.py
│   ├── confirmation_dialog.py
│   └── ipc_client.py
├── shared/
│   └── message_protocol.py
└── main.py
```

## Core behavior

- **Modes**
  - `PASSIVE`: build plan only, no execution.
  - `ASSISTED`: confirmation before every step.
  - `ACTIVE`: auto-run non-critical steps, confirm critical.
- **Critical actions** are detected by `security.py` (delete/move, `.exe` download, mass actions, password-like fields, sensitive paths, banking hints).
- **Kill switch** (`Ctrl+Alt+X` in GUI when `keyboard` lib available) sends `KILL_SIGNAL`, agent stops current execution, clears queue, and switches to `PASSIVE`.
- **Logging** writes JSONL audit events to `logs/aia_audit.jsonl`.

## Installation

> Python 3.11+ required. Recommended: Windows 11.

```powershell
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
pip install PySide6 pystray pillow requests pyautogui pywin32 keyboard vosk sounddevice
```

Set Gemini API key:

```powershell
setx GEMINI_API_KEY "your_api_key_here"
```

## Run

### Option A: start both via launcher

```powershell
python -m aia.main --component all
```

### Option B: separate processes (recommended)

Terminal 1:
```powershell
python -m aia.main --component agent
```

Terminal 2:
```powershell
python -m aia.main --component gui
```

## Notes

- `voice.py` supports Vosk when model/dependencies are present, otherwise works as text-fallback queue.
- `executor.py` uses safe action wrappers and returns structured `{ok, error}` responses.
- If GUI closes, the **agent process keeps running** when launched separately.

## UI/UX Design System

- Comprehensive visual and motion specification is documented in `docs/UI_UX_DESIGN_SYSTEM.md`.
- Implemented Fluent-inspired glassmorphism shell, mode-based accent transitions, pill/panel morphing, voice visualizer, critical confirmation modal, and panic flash behavior in PySide6 GUI layer.
