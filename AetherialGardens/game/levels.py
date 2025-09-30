"""game/levels.py – simple data container for the Level‑Select screen."""

from pathlib import Path
from typing import NamedTuple

class LevelInfo(NamedTuple):
    """Immutable description of a single puzzle level."""
    name: str          # Friendly name shown in the UI
    rows: int          # Number of rows (same as columns for square puzzles)
    bg_path: Path      # Path to the background image (relative to project root)

# ---------------------------------------------------------------------
# Starter levels – add more entries here whenever you create a new garden.
# ---------------------------------------------------------------------
LEVELS = [
    LevelInfo(
        name="Aetherial – 3 × 3",
        rows=3,
        bg_path=Path("assets/images/garden_3x3.png"),
    ),
    LevelInfo(
        name="Aetherial – 4 × 4",
        rows=4,
        bg_path=Path("assets/images/garden_4x4.png"),
    ),
    LevelInfo(
        name="Aetherial – 5 × 5",
        rows=5,
        bg_path=Path("assets/images/garden_5x5.png"),
    ),
]