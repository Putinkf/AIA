from __future__ import annotations

import argparse
import multiprocessing as mp


def run_agent_component() -> None:
    from aia.agent.main_agent import run_agent

    run_agent()


def run_gui_component() -> None:
    try:
        from aia.gui.main_gui import run_gui
    except ModuleNotFoundError as exc:
        if exc.name == "PySide6":
            raise SystemExit(
                "PySide6 is not installed. Install GUI dependencies, for example:\n"
                "pip install PySide6 pystray pillow keyboard"
            ) from exc
        raise
    run_gui()


def run_all() -> None:
    agent_proc = mp.Process(target=run_agent_component, daemon=True)
    agent_proc.start()
    run_gui_component()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIA launcher")
    parser.add_argument("--component", choices=["agent", "gui", "all"], default="all")
    args = parser.parse_args()

    if args.component == "agent":
        run_agent_component()
    elif args.component == "gui":
        run_gui_component()
    else:
        run_all()
