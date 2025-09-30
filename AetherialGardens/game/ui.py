"""game/ui.py – tiny UI helpers for the MVP.
Only pygame is used; everything stays under 150 lines.
"""


import pygame
from typing import Callable, Tuple

# ------------------------------------------------------------
# Button – rectangular clickable UI element.
# ------------------------------------------------------------
class Button:
    def __init__(self, rect: pygame.Rect, text: str, callback: Callable[[], None],
                 bg_color: Tuple[int, int, int] = (70, 120, 90),
                 txt_color: Tuple[int, int, int] = (255, 255, 255)):
        self.rect = rect
        self.text = text
        self.callback = callback
        self.bg_color = bg_color
        self.txt_color = txt_color
        self.font = pygame.font.SysFont(None, 48)

    def draw(self, surf: pygame.Surface) -> None:
        pygame.draw.rect(surf, self.bg_color, self.rect, border_radius=8)
        pygame.draw.rect(surf, (30, 60, 45), self.rect, 2, border_radius=8)
        txt_surf = self.font.render(self.text, True, self.txt_color)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surf.blit(txt_surf, txt_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

# ------------------------------------------------------------
# Menu – collection of Buttons shown before the game starts.
# ------------------------------------------------------------
class Menu:
    def __init__(self, screen_rect: pygame.Rect, start_cb: Callable[[], None], quit_cb: Callable[[], None]):
        w, h = screen_rect.size
        btn_w, btn_h = 250, 60
        spacing = 20
        center_x = w // 2
        start_rect = pygame.Rect(0, 0, btn_w, btn_h)
        start_rect.center = (center_x, h // 2 - spacing)
        quit_rect = pygame.Rect(0, 0, btn_w, btn_h)
        quit_rect.center = (center_x, h // 2 + spacing)
        self.buttons = [
            Button(start_rect, "Start", start_cb),
            Button(quit_rect, "Quit", quit_cb),
        ]
        self.title_font = pygame.font.SysFont(None, 72)

    def draw(self, surf: pygame.Surface) -> None:
        # Dark overlay background
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))
        # Title text
        title = self.title_font.render("Aetherial", True, (200, 230, 200))
        title_rect = title.get_rect(center=(surf.get_width() // 2, surf.get_height() // 3))
        surf.blit(title, title_rect)
        # Buttons
        for btn in self.buttons:
            btn.draw(surf)

    def handle_event(self, event: pygame.event.Event) -> None:
        for btn in self.buttons:
            btn.handle_event(event)

# ------------------------------------------------------------
# HUD – tiny heads‑up‑display during gameplay (move counter & pause).
# ------------------------------------------------------------
class HUD:
    def __init__(self, screen_rect: pygame.Rect, pause_cb: Callable[[], None]):
        self.move_count = 0
        self.pause_cb = pause_cb
        # Pause button (small square in top‑right)
        size = 40
        self.pause_rect = pygame.Rect(screen_rect.right - size - 10, 10, size, size)
        self.font = pygame.font.SysFont(None, 36)

    def increment_moves(self) -> None:
        self.move_count += 1

    def draw(self, surf: pygame.Surface) -> None:
        # Move counter (top‑left)
        counter = self.font.render(f"Moves: {self.move_count}", True, (230, 230, 230))
        surf.blit(counter, (10, 10))
        # Pause button (simple II symbol)
        pygame.draw.rect(surf, (80, 100, 80), self.pause_rect, border_radius=5)
        pygame.draw.rect(surf, (30, 50, 30), self.pause_rect, 2, border_radius=5)
        pause_sym = self.font.render("II", True, (255, 255, 255))
        sym_rect = pause_sym.get_rect(center=self.pause_rect.center)
        surf.blit(pause_sym, sym_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_rect.collidepoint(event.pos):
                self.pause_cb()


# ------------------------------------------------------------
# LevelSelect – shows a button for each entry in `levels.LEVELS`.
# Also displays the best‑move count and best‑star rating saved in
# `save_data.json`.
# ------------------------------------------------------------
class LevelSelect:
    """
    UI screen that lets the player choose a garden size and shows
    the best performance for each level (moves + stars).
    """

    def __init__(self, screen_rect: pygame.Rect, start_cb, back_cb):
        # -----------------------------------------------------------------
        # Imports that are needed only here (avoid circular imports)
        # -----------------------------------------------------------------
        from .save import load_progress, star_key
        from .star import StarHUD

        # -----------------------------------------------------------------
        # Load persisted progress (once, when the screen is created)
        # -----------------------------------------------------------------
        self.progress = load_progress()                 # {"best_moves": {}, "best_stars": {}}
        self.star_key = star_key                       # helper to build "3x3", "4x4", …

        # -----------------------------------------------------------------
        # Build UI elements
        # -----------------------------------------------------------------
        from .levels import LEVELS
        self.levels = LEVELS

        self.start_cb = start_cb
        self.back_cb = back_cb
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
        self.small_font = pygame.font.SysFont(None, 28)  # For stats text

        # Button geometry – increased height to accommodate stats
        btn_w, btn_h = 320, 90
        spacing = 30  # Increased spacing between buttons
        total_h = len(self.levels) * (btn_h + spacing) - spacing
        # Position buttons lower to avoid title overlap
        start_y = (screen_rect.height - total_h) // 2 + 50
        center_x = screen_rect.centerx

        self.buttons = []          # list of (rect, LevelInfo)
        for idx, lvl in enumerate(self.levels):
            r = pygame.Rect(0, 0, btn_w, btn_h)
            r.centerx = center_x
            r.y = start_y + idx * (btn_h + spacing)
            self.buttons.append((r, lvl))

        # Back button with better styling
        back_btn_width, back_btn_height = 80, 35
        self.back_rect = pygame.Rect(
            15, 15, back_btn_width, back_btn_height
        )

        # Re‑use the star‑drawing helper for the small thumbnails
        # Pass screen_rect instead of WINDOW_SIZE directly
        self.star_hud = StarHUD(pygame.Rect(0, 0, *screen_rect.size))

        # Track mouse position for hover effects
        self.hovered_button = None

    # -----------------------------------------------------------------
    # Helper: draw a tiny row of stars (0‑3) next to a level entry
    # -----------------------------------------------------------------
    def _draw_small_stars(self, surf: pygame.Surface, center: tuple[int, int], rating: int):
        """Draw 0‑3 gold stars of a reduced size (radius = 8)."""
        star_radius = 8
        spacing = 5
        for i in range(rating):
            cx = center[0] + i * (star_radius * 2 + spacing) - ((rating - 1) * (star_radius * 2 + spacing)) // 2
            points = []
            for j in range(10):
                ang = j * 36
                rad = star_radius if j % 2 == 0 else star_radius // 2
                vec = pygame.math.Vector2(1, 0).rotate(ang) * rad
                points.append((cx + int(vec.x), center[1] + int(vec.y)))
            pygame.draw.polygon(surf, (255, 215, 0), points)

    # -----------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------
    def draw(self, surf: pygame.Surface) -> None:
        # Aetherial garden themed background
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        # Deep forest green to dark blue gradient overlay
        overlay.fill((5, 25, 15, 200))
        surf.blit(overlay, (0, 0))

        # Title positioned higher to avoid overlap
        title = self.title_font.render("Select a Garden", True, (180, 230, 180))
        # Position title higher on screen
        title_rect = title.get_rect(center=(surf.get_width() // 2, 80))
        # Add a subtle glow effect around the title
        title_glow = self.title_font.render("Select a Garden", True, (100, 180, 100))
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            surf.blit(title_glow, (title_rect.x + dx, title_rect.y + dy))
        surf.blit(title, title_rect)

        # Level buttons + saved stats
        for idx, (rect, lvl) in enumerate(self.buttons):
            # Determine if this button is being hovered
            is_hovered = self.hovered_button == idx
            
            # Button background with nature-themed colors
            bg_color = (85, 140, 110) if is_hovered else (70, 120, 100)
            border_color = (40, 80, 65) if not is_hovered else (60, 110, 85)
            
            pygame.draw.rect(surf, bg_color, rect, border_radius=12)
            pygame.draw.rect(surf, border_color, rect, 2, border_radius=12)
            
            # Add subtle inner shadow for depth
            inner_rect = pygame.Rect(
                rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4
            )
            pygame.draw.rect(surf, (60, 100, 85), inner_rect, 1, border_radius=10)

            # Button label (e.g., “Garden – 3 × 3”) - left aligned
            txt = self.font.render(lvl.name, True, (240, 250, 230))
            txt_rect = txt.get_rect(midleft=(rect.left + 20, rect.centery - 10))
            surf.blit(txt, txt_rect)

            # ------- draw saved best moves (right side of button) -------
            size_key = self.star_key(lvl.rows)
            best_moves = self.progress["best_moves"].get(size_key)
            if best_moves is not None:
                moves_txt = self.small_font.render(f"Best: {best_moves}", True, (220, 240, 200))
                moves_rect = moves_txt.get_rect(midright=(rect.right - 15, rect.centery - 10))
                surf.blit(moves_txt, moves_rect)
            else:
                # Show "Not solved" or keep space empty
                placeholder_txt = self.small_font.render("-", True, (150, 170, 150))
                placeholder_rect = placeholder_txt.get_rect(midright=(rect.right - 15, rect.centery - 10))
                surf.blit(placeholder_txt, placeholder_rect)

            # ------- draw saved best stars (centered below the name/moves) -------
            best_stars = self.progress["best_stars"].get(size_key, 0)
            # Position stars centered below the level name and move count
            star_center = (rect.centerx, rect.centery + 15)
            self._draw_small_stars(surf, star_center, best_stars)

        # Styled back button matching the theme
        pygame.draw.rect(surf, (45, 85, 65), self.back_rect, border_radius=8)
        pygame.draw.rect(surf, (30, 60, 45), self.back_rect, 2, border_radius=8)
        back_txt = self.small_font.render("Back", True, (220, 240, 220))
        back_txt_rect = back_txt.get_rect(center=self.back_rect.center)
        surf.blit(back_txt, back_txt_rect)

    # -----------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEMOTION:
            # Track which button is being hovered over
            mouse_pos = event.pos
            for idx, (rect, lvl) in enumerate(self.buttons):
                if rect.collidepoint(mouse_pos):
                    self.hovered_button = idx
                    return
            self.hovered_button = None
        
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        # Click on a level button?
        for rect, lvl in self.buttons:
            if rect.collidepoint(event.pos):
                self.start_cb(lvl)
                return
        # Click on Back?
        if self.back_rect.collidepoint(event.pos):
            self.back_cb()