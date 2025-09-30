"""game/save.py – simple JSON‑based persistence for the MVP.
Only the built‑in `json` and `os` modules are used.
"""

import json
import os
from typing import Dict, Any

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "save_data.json")

def _ensure_file() -> None:
    """Create the file with default values if it does not exist."""
    if not os.path.isfile(SAVE_PATH):
        default = {"best_moves": None, "unlocked": True}
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

def load_progress() -> Dict[str, Any]:
    """Return the saved dictionary; guarantees keys exist."""
    _ensure_file()
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Ensure expected keys are present (future‑proofing)
    data.setdefault("best_moves", None)
    data.setdefault("unlocked", True)
    return data

def save_progress(data: Dict[str, Any]) -> None:
    """Overwrite the JSON file with the supplied dictionary."""
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)