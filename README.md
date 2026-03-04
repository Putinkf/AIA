# AIA (AI Agent Assistant)

> Windows-only desktop AI assistant with **two-process architecture** (Agent + GUI) and local IPC.

---

## 🇷🇺 Русская версия

## Что это

AIA — это MVP настольного AI-ассистента для Windows:

- **Фоновый процесс Agent**: принимает команды (голос/текст), строит план через Gemini, проверяет критичность шагов, выполняет действия и пишет аудит-логи.
- **GUI-процесс**: чат, логи, переключение режимов, системный трей, модалки подтверждения и Kill Switch.
- **IPC**: обмен сообщениями по `127.0.0.1:8765` (JSON Lines протокол).

## Структура проекта

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
│   ├── design_system.py
│   └── ipc_client.py
├── shared/
│   └── message_protocol.py
└── main.py
```

## Режимы работы

- `PASSIVE` — только планирование, без выполнения.
- `ASSISTED` — подтверждение **каждого** шага.
- `ACTIVE` — авто-выполнение, но подтверждение критических шагов.

## Требования

- Windows 10/11
- Python **3.11+**
- Для GUI нужен `PySide6`

## Установка (пошагово)

### 1) Клонирование и переход в проект

```powershell
git clone <repo_url>
cd AIA
```

### 2) Создание и активация venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3) Установка зависимостей

Минимум для агента:

```powershell
pip install requests
```

Для GUI и полного MVP:

```powershell
pip install -r requirements.txt
```

или явно:

```powershell
pip install PySide6 pystray pillow requests pyautogui pywin32 keyboard vosk sounddevice
```

### 4) Настройка Gemini API key

```powershell
setx GEMINI_API_KEY "YOUR_REAL_KEY"
```

⚠️ Важно:
- `setx` применится **только в новых терминалах**.
- После `setx` закройте текущий PowerShell и откройте новый.
- Проверьте значение:

```powershell
$env:GEMINI_API_KEY
```

## Запуск (подробно)

### Вариант A — два отдельных процесса (рекомендуется)

Терминал №1 (Agent):

```powershell
python -m aia.main --component agent
```

Терминал №2 (GUI):

```powershell
python -m aia.main --component gui
```

### Вариант B — один лаунчер

```powershell
python -m aia.main --component all
```

## Частые ошибки и решения

### 1) `ModuleNotFoundError: No module named 'aia'`

Причина: команда запущена не из корня проекта.

Решение:

```powershell
cd C:\path\to\AIA
python -m aia.main --component agent
```

### 2) `ModuleNotFoundError: No module named 'PySide6'`

Причина: не установлены GUI-зависимости.

Решение:

```powershell
pip install PySide6 pystray pillow keyboard
```

Теперь `--component agent` может запускаться и без PySide6, а `--component gui` требует PySide6.

### 3) Ошибка в `eventFilter` (`QEvent has no attribute MouseButtonPress`)

Исправлено в коде: используется `QEvent.Type.MouseButtonPress` / `QEvent.Type.MouseMove`.

### 4) Предупреждение DPI от Qt

Сообщение вида `SetProcessDpiAwarenessContext() failed` обычно предупреждение среды/прав, не всегда критично для работы.

## Логирование

Аудит-лог: `logs/aia_audit.jsonl`.

Содержит: timestamp, режим, команды, план, выполненные шаги, ошибки, подтверждения.

## UI/UX дизайн-система

- Документ: `docs/UI_UX_DESIGN_SYSTEM.md`
- Реализованы Fluent-inspired glassmorphism, mode-accent transitions, pill/panel morph, confirmation modal и panic flash.

---

## 🇬🇧 English version (short)

AIA is a Windows desktop AI assistant with two processes:

1. Agent (`aia/agent`) for planning/execution/security/logging.
2. GUI (`aia/gui`) for chat, modes, tray, confirmations, and kill switch.

Install:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
setx GEMINI_API_KEY "YOUR_REAL_KEY"
```

Run (recommended, separate terminals):

```powershell
python -m aia.main --component agent
python -m aia.main --component gui
```

If GUI fails with missing PySide6:

```powershell
pip install PySide6 pystray pillow keyboard
```
