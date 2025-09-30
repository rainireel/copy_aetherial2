"""game/save.py – JSON persistence for best moves and best star rating."""

import json
import os
from typing import Dict, Any

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "save_data.json")


def _ensure_file() -> None:
    """Create the file with defaults if it does not exist."""
    if not os.path.isfile(SAVE_PATH):
        default = {
            "best_moves": {},      # e.g., {"3x3": 18, "4x4": 45}
            "best_stars": {},      # e.g., {"3x3": 3, "4x4": 2}
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)


def load_progress() -> Dict[str, Any]:
    """Read the JSON file and guarantee the expected keys exist."""
    _ensure_file()
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure new format structures exist
    data.setdefault("best_moves", {})
    data.setdefault("best_stars", {})
    
    # Migrate old format entries if they exist (from previous implementations)
    # This handles any legacy keys that might still exist
    for size in [3, 4, 5]:
        size_key = f"{size}x{size}"
        # Check for old-style keys and migrate them
        old_best_key = f"best_{size_key}"
        old_star_key = f"stars_{size_key}"
        
        if old_best_key in data and data[old_best_key] is not None:
            data["best_moves"][size_key] = data[old_best_key]
            
        if old_star_key in data and data[old_star_key] is not None:
            data["best_stars"][size_key] = data[old_star_key]

    return data


def save_progress(data: Dict[str, Any]) -> None:
    """Overwrite the JSON file with the supplied dictionary."""
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def star_key(size: int) -> str:
    """Utility: turn a board size into the dict key used in JSON."""
    return f"{size}x{size}"