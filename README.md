# AIA (AI Agent Assistant) MVP

> Windows-only desktop AI assistant with **two-process architecture** (Agent + GUI) and local IPC.

---

## 🇷🇺 Описание проекта

AIA — это настольный AI-ассистент для Windows с разделением логики и интерфейса:

* **Фоновый процесс Agent**: Слушает голос/текст, планирует задачи через Gemini 1.5 Flash, проверяет безопасность шагов и выполняет их (эмуляция мыши/клавиатуры).
* **GUI-процесс**: Современный интерфейс на PySide6, управление режимами, логи и экстренная остановка (Kill Switch).
* **Безопасность**: Три режима работы (`PASSIVE`, `ASSISTED`, `ACTIVE`) с обязательным подтверждением критических действий.

---

## 🧱 Project Structure / Структура проекта

```text
aia/
├── agent/
│   ├── main_agent.py      # Точка входа агента
│   ├── planner.py         # Интеграция с Gemini API
│   ├── executor.py        # Управление мышью/клавиатурой
│   ├── security.py        # Валидация действий
│   ├── voice.py           # Распознавание речи (Vosk)
│   ├── logger.py          # Аудит-логи (JSONL)
│   └── ipc_server.py      # Сервер обмена сообщениями
├── gui/
│   ├── main_gui.py        # Главное окно PySide6
│   ├── chat_widget.py     # Интерфейс чата
│   ├── tray.py            # Системный трей
│   ├── confirmation_dialog.py # Модалки безопасности
│   ├── design_system.py   # Стили и анимации
│   └── ipc_client.py      # Клиент обмена сообщениями
├── shared/
│   └── message_protocol.py # Общий протокол JSON IPC
└── main.py                # Общий лаунчер компонентов

```

---

## ⚙️ Installation / Установка

**Requirements:** Windows 10/11, Python 3.11+.

1. **Clone & Environment:**
```powershell
git clone <repo_url>
cd AIA
python -m venv .venv
.\.venv\Scripts\Activate.ps1

```


2. **Dependencies:**
```powershell
pip install PySide6 pystray pillow requests pyautogui pywin32 keyboard vosk sounddevice

```


3. **API Key:**
```powershell
setx GEMINI_API_KEY "YOUR_ACTUAL_KEY"
# Перезапустите терминал после этой команды!

```



---

## 🚀 How to Run / Как запустить

### Option A: Separate Processes (Recommended for Debugging)

**Terminal 1 (Agent):**

```powershell
python -m aia.main --component agent

```

**Terminal 2 (GUI):**

```powershell
python -m aia.main --component gui

```

### Option B: All-in-one Launcher

```powershell
python -m aia.main --component all

```

---

## 🛠 Operation Modes / Режимы работы

| Mode | Description | Safety |
| --- | --- | --- |
| **🟢 PASSIVE** | Only generates a plan. | No execution. |
| **🟡 ASSISTED** | Confirms **every** single step with user. | High safety. |
| **🔴 ACTIVE** | Executes automatically. | Confirms **critical** steps only. |

**Kill Switch:** Press `Ctrl+Alt+X` to immediately stop all actions and switch to Passive mode.

---

## 📜 Logging / Логирование

All actions are stored in `logs/aia_audit.jsonl`. It includes timestamps, modes, plans, and security decisions.

---