from __future__ import annotations
import os, pathlib

# Constant output filename for all consumer apps
DB_JSON_PATH = os.path.join("assets", "nervon_workflow.json")

# Where to store historical snapshots
HISTORY_DIR = os.path.join("assets", "history")

def ensure_dirs() -> None:
    pathlib.Path("assets").mkdir(exist_ok=True, parents=True)
    pathlib.Path(HISTORY_DIR).mkdir(exist_ok=True, parents=True)
