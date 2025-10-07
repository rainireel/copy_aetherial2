"""game/save.py – JSON persistence for best moves, stars, and audio settings."""

import json
import os
from typing import Dict, Any

SAVE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "save_data.json")


def _ensure_file() -> None:
    """Create the file with defaults if it does not exist."""
    if not os.path.isfile(SAVE_PATH):
        default = {
            "volume": 0.4,             # music & SFX volume (0.0 – 1.0)
            "muted": False,            # global mute flag
        }
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)


def load_progress() -> Dict[str, Any]:
    """Read the JSON file and guarantee the expected keys exist."""
    _ensure_file()
    with open(SAVE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Ensure every key we expect is present (future‑proofing)
    # Remove best moves and best stars tracking
    data.setdefault("volume", 0.4)
    data.setdefault("muted", False)
    return data


def save_progress(data: Dict[str, Any]) -> None:
    """Overwrite the JSON file with the supplied dictionary."""
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def star_key(size: int) -> str:
    """Utility: turn a board size into the dict key used in JSON."""
    return f"{size}x{size}"