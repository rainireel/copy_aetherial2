"""game/assets.py – Asset path management."""

from pathlib import Path

def get_path(filename: str) -> str:
    """Get the absolute path to an asset file."""
    return str(Path(__file__).parent.parent / filename)
