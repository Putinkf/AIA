from __future__ import annotations

import argparse
import multiprocessing as mp

from aia.agent.main_agent import run_agent
from aia.gui.main_gui import run_gui


def run_all() -> None:
    agent_proc = mp.Process(target=run_agent, daemon=True)
    agent_proc.start()
    run_gui()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AIA launcher")
    parser.add_argument("--component", choices=["agent", "gui", "all"], default="all")
    args = parser.parse_args()

    if args.component == "agent":
        run_agent()
    elif args.component == "gui":
        run_gui()
    else:
        run_all()
