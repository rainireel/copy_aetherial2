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
        # Initialize with best moves for different board sizes
        default = {
            "best_3x3": None,
            "best_4x4": None, 
            "best_5x5": None,
            "unlocked": True
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)

def load_progress() -> Dict[str, Any]:
    """Return the saved dictionary; guarantees keys exist."""
    _ensure_file()
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Handle old format (with best_moves dict) and convert to new format
    if "best_moves" in data and isinstance(data["best_moves"], dict):
        # Old format - convert to new format
        old_best_moves = data["best_moves"]
        data["best_3x3"] = old_best_moves.get("3x3")
        data["best_4x4"] = old_best_moves.get("4x4") 
        data["best_5x5"] = old_best_moves.get("5x5")
        # Remove the old format
        del data["best_moves"]
    
    # Ensure all board sizes are present in new format
    data.setdefault("best_3x3", None)
    data.setdefault("best_4x4", None)
    data.setdefault("best_5x5", None)
    data.setdefault("unlocked", True)
    return data

def save_progress(data: Dict[str, Any]) -> None:
    """Overwrite the JSON file with the supplied dictionary."""
    # Ensure we're not saving in the old format
    if "best_moves" in data and isinstance(data["best_moves"], dict):
        # Convert from old to new format if somehow present
        old_best_moves = data["best_moves"]
        data["best_3x3"] = old_best_moves.get("3x3", data.get("best_3x3"))
        data["best_4x4"] = old_best_moves.get("4x4", data.get("best_4x4"))
        data["best_5x5"] = old_best_moves.get("5x5", data.get("best_5x5"))
        del data["best_moves"]
    
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)