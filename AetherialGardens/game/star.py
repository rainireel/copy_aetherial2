"""game/star.py – draw a 0‑3 star rating and compute it.

Stars are simple gold polygons (5‑point). The rating thresholds are
hard‑coded per board size but can be tweaked later in the
`STAR_THRESHOLDS` dictionary.
"""

import pygame
from typing import Tuple

# -----------------------------------------------------------------
# Hard‑coded thresholds (moves needed for 3‑star and 2‑star ratings)
# Format: size → (max_moves_for_3_stars, max_moves_for_2_stars)
# Anything above the second value gets 1 star.
# -----------------------------------------------------------------
STAR_THRESHOLDS = {
    3: (20, 30),   # 3×3 board: ≤20 moves → 3★, ≤30 → 2★, else 1★
    4: (40, 60),   # 4×4 board
    5: (80, 120),  # 5×5 board
}


def _make_star_points(center: Tuple[int, int], radius: int) -> Tuple[Tuple[int, int], ...]:
    """Return the 5‑point star polygon used for drawing."""
    import math
    cx, cy = center
    points = []
    for i in range(10):
        angle = i * 36  # 360° / 10
        rad = radius if i % 2 == 0 else radius // 2
        # Convert to radians and calculate point
        radian = math.radians(angle)
        x = cx + rad * math.cos(radian)
        y = cy + rad * math.sin(radian)
        points.append((int(x), int(y)))
    return tuple(points)


class StarHUD:
    """Draws a row of 0‑3 gold stars in the top‑right corner."""
    def __init__(self, screen_rect: pygame.Rect):
        self.screen_rect = screen_rect
        self.rating = 0          # 0‑3
        self.font = pygame.font.SysFont(None, 24)

    def set_rating(self, rating: int) -> None:
        """Clamp rating to 0‑3 and store it."""
        self.rating = max(0, min(3, rating))

    def draw(self, surf: pygame.Surface) -> None:
        """Render the stars (filled gold) and the numeric rating."""
        if self.rating <= 0:
            return  # Don't draw anything if rating is 0
            
        # Position: a little inset from the top‑right corner
        star_radius = 12
        spacing = 5
        total_width = self.rating * (star_radius * 2 + spacing) - spacing
        start_x = self.screen_rect.right - total_width - 10
        y = 10

        gold = (255, 215, 0)
        for i in range(self.rating):
            cx = start_x + i * (star_radius * 2 + spacing) + star_radius
            points = _make_star_points((cx, y + star_radius), star_radius)
            pygame.draw.polygon(surf, gold, points)

        # Show the numeric value next to the stars (optional)
        txt = self.font.render(f"{self.rating}/3", True, (230, 230, 230))
        txt_rect = txt.get_rect(midleft=(start_x + total_width + 8, y + star_radius))
        surf.blit(txt, txt_rect)

    @staticmethod
    def compute_rating(board_size: int, move_count: int) -> int:
        """Return 1‑3 based on `STAR_THRESHOLDS`. Guarantees at least 1 star."""
        thr_3, thr_2 = STAR_THRESHOLDS.get(board_size, (float("inf"), float("inf")))
        if move_count <= thr_3:
            return 3
        if move_count <= thr_2:
            return 2
        return 1