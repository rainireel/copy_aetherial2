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
        # Pixel-style fonts (using system fonts to simulate pixel style)
        self.font = pygame.font.SysFont('monospace', 28, bold=True)
        self.title_font = pygame.font.SysFont('monospace', 40, bold=True)
        self.small_font = pygame.font.SysFont('monospace', 22)  # For stats text
        self.status_font = pygame.font.SysFont('monospace', 20, bold=True)  # For status text

        # Button geometry – increased height to accommodate stats
        btn_w, btn_h = 330, 100
        spacing = 40  # Increased spacing between buttons
        total_h = len(self.levels) * (btn_h + spacing) - spacing
        # Position buttons lower to avoid title overlap
        start_y = (screen_rect.height - total_h) // 2 + 70
        center_x = screen_rect.centerx

        self.buttons = []          # list of (rect, LevelInfo)
        for idx, lvl in enumerate(self.levels):
            r = pygame.Rect(0, 0, btn_w, btn_h)
            r.centerx = center_x
            r.y = start_y + idx * (btn_h + spacing)
            self.buttons.append((r, lvl))

        # Back button with better styling
        back_btn_width, back_btn_height = 90, 40
        self.back_rect = pygame.Rect(
            15, 15, back_btn_width, back_btn_height
        )

        # Re‑use the star‑drawing helper for the small thumbnails
        # Pass screen_rect instead of WINDOW_SIZE directly
        self.star_hud = StarHUD(pygame.Rect(0, 0, *screen_rect.size))

        # Track mouse position for hover effects
        self.hovered_button = None

        # Time tracking for animations
        self.last_star_animation = pygame.time.get_ticks()
        self.star_frame = 0

    # -----------------------------------------------------------------
    # Helper: draw pixel-style small stars with animation
    # -----------------------------------------------------------------
    def _draw_small_stars(self, surf: pygame.Surface, center: tuple[int, int], rating: int, is_hovered=False):
        """Draw 0‑3 gold stars in pixel art style with optional animation."""
        star_size = 10  # pixel size
        spacing = 6
        
        for i in range(rating):
            # Calculate x position for each star
            total_width = rating * star_size + (rating - 1) * spacing
            start_x = center[0] - total_width // 2
            
            star_x = start_x + i * (star_size + spacing)
            star_y = center[1] - star_size // 2
            
            # Draw a pixel-style star
            star_color = (255, 215, 0)  # Gold color
            if is_hovered:
                # Brighten hover effect
                star_color = (255, 230, 100)
            
            # Draw star as a pixel-art style shape (a small star made of pixels)
            # Center point
            pygame.draw.rect(surf, star_color, (star_x + 4, star_y + 1, 2, 2))
            pygame.draw.rect(surf, star_color, (star_x + 3, star_y + 2, 4, 2))
            pygame.draw.rect(surf, star_color, (star_x + 2, star_y + 3, 6, 2))
            pygame.draw.rect(surf, star_color, (star_x + 1, star_y + 4, 8, 2))
            pygame.draw.rect(surf, star_color, (star_x + 2, star_y + 5, 6, 2))
            pygame.draw.rect(surf, star_color, (star_x + 3, star_y + 6, 4, 2))
            pygame.draw.rect(surf, star_color, (star_x + 4, star_y + 7, 2, 2))

    # -----------------------------------------------------------------
    # Draw pixel-style difficulty icons
    # -----------------------------------------------------------------
    def _draw_difficulty_icon(self, surf: pygame.Surface, pos: tuple[int, int], level_size: int):
        """Draw pixel art icons representing difficulty."""
        x, y = pos
        icon_color = (100, 180, 80)  # Green
        
        if level_size == 3:  # 3x3 - easy: sprout
            # Pixel art sprout
            pygame.draw.rect(surf, (120, 90, 40), (x + 4, y + 8, 2, 4))  # stem
            pygame.draw.circle(surf, icon_color, (x + 3, y + 7), 2)  # left leaf
            pygame.draw.circle(surf, icon_color, (x + 7, y + 7), 2)  # right leaf
        elif level_size == 4:  # 4x4 - medium: bush
            # Pixel art bush
            pygame.draw.circle(surf, icon_color, (x + 5, y + 6), 4)
        elif level_size == 5:  # 5x5 - hard: tree
            # Pixel art tree
            pygame.draw.rect(surf, (120, 90, 40), (x + 4, y + 6, 2, 4))  # trunk
            pygame.draw.circle(surf, icon_color, (x + 5, y + 5), 4)  # leaves

    # -----------------------------------------------------------------
    # Draw pixel-style lock icon for locked levels
    # -----------------------------------------------------------------
    def _draw_lock_icon(self, surf: pygame.Surface, pos: tuple[int, int]):
        """Draw pixel art lock icon for locked levels."""
        x, y = pos
        # Simple pixel art lock
        lock_color = (150, 150, 150)
        # Draw lock base
        pygame.draw.rect(surf, lock_color, (x + 3, y + 5, 6, 5))
        # Draw lock loop
        pygame.draw.rect(surf, lock_color, (x + 4, y + 3, 4, 2))
        pygame.draw.rect(surf, lock_color, (x + 3, y + 3, 2, 2))
        pygame.draw.rect(surf, lock_color, (x + 7, y + 3, 2, 2))

    # -----------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------
    def draw(self, surf: pygame.Surface) -> None:
        # Pixel-style garden background (dark green with subtle pattern)
        overlay = pygame.Surface(surf.get_size())
        overlay.fill((5, 25, 15))  # Dark green background
        # Add subtle grid pattern to simulate pixel background
        for y in range(0, surf.get_height(), 20):
            for x in range(0, surf.get_width(), 20):
                if (x // 20 + y // 20) % 2 == 0:
                    pygame.draw.rect(overlay, (8, 30, 20), (x, y, 10, 10))
        surf.blit(overlay, (0, 0))

        # Title with enhanced fantasy theme
        title = self.title_font.render("AETHERIAL GARDENS", True, (180, 220, 150))  # Pastel green
        title_rect = title.get_rect(center=(surf.get_width() // 2, 80))
        
        # Enhanced pixel-style outline with fantasy glow effect
        for dx in [-2, -1, 0, 1, 2]:
            for dy in [-2, -1, 0, 1, 2]:
                if dx != 0 or dy != 0:  # Skip the center
                    # Create a glowing effect with different colors based on distance
                    if abs(dx) + abs(dy) <= 1:
                        outline_color = (60, 110, 70)  # Inner glow
                    elif abs(dx) + abs(dy) <= 2:
                        outline_color = (30, 60, 40)   # Outer glow
                    else:
                        outline_color = (15, 30, 20)   # Even further glow
                    outline = self.title_font.render("AETHERIAL GARDENS", True, outline_color)
                    surf.blit(outline, (title_rect.x + dx, title_rect.y + dy))
        
        # Add magical shimmer effect to title text
        surf.blit(title, title_rect)

        # Level buttons + saved stats
        current_time = pygame.time.get_ticks()
        # Animate stars every 500ms
        if current_time - self.last_star_animation > 500:
            self.star_frame = (self.star_frame + 1) % 3
            self.last_star_animation = current_time

        for idx, (rect, lvl) in enumerate(self.buttons):
            # Determine if this button is being hovered
            is_hovered = self.hovered_button == idx
            
            # Button background with pixel-style wooden frame
            bg_color = (120, 100, 70) if is_hovered else (100, 85, 60)  # Wood brown tones
            border_color = (70, 55, 35) if not is_hovered else (140, 120, 90)
            
            # Draw pixel-style button with wooden frame
            pygame.draw.rect(surf, bg_color, rect)
            # Inner border for more pixel-art style
            inner_rect = pygame.Rect(rect.x + 5, rect.y + 5, rect.width - 10, rect.height - 10)  # Increased padding
            pygame.draw.rect(surf, (130, 110, 90), inner_rect)
            
            # Draw pixel-art frame with enhanced corners
            pygame.draw.rect(surf, border_color, rect, 2)
            # Additional pixel-style corner details
            pygame.draw.rect(surf, border_color, (rect.x, rect.y, 4, 2))
            pygame.draw.rect(surf, border_color, (rect.x, rect.y, 2, 4))
            pygame.draw.rect(surf, border_color, (rect.right - 4, rect.y, 4, 2))
            pygame.draw.rect(surf, border_color, (rect.right - 2, rect.y, 2, 4))
            pygame.draw.rect(surf, border_color, (rect.x, rect.bottom - 2, 4, 2))
            pygame.draw.rect(surf, border_color, (rect.x, rect.bottom - 4, 2, 4))
            pygame.draw.rect(surf, border_color, (rect.right - 4, rect.bottom - 2, 4, 2))
            pygame.draw.rect(surf, border_color, (rect.right - 2, rect.bottom - 4, 2, 4))

            # Button label (e.g., “Garden – 3 × 3”) - top row, left aligned with more padding
            txt = self.font.render(lvl.name, True, (240, 250, 200))  # Light beige
            # Pixel-style outline for button text
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    outline_txt = self.font.render(lvl.name, True, (80, 70, 60))
                    surf.blit(outline_txt, (rect.left + 30 + dx, rect.top + 20 + dy))  # More padding from top
            surf.blit(txt, (rect.left + 30, rect.top + 20))

            # Draw difficulty icon to the right of the name
            self._draw_difficulty_icon(surf, (rect.right - 100, rect.top + 22), lvl.rows)

            # Status row: best moves (right aligned in button) - separate from title row
            size_key = self.star_key(lvl.rows)
            best_moves = self.progress["best_moves"].get(size_key)
            
            if best_moves is not None:
                # Create a separate area for the status text to separate it from the button label
                moves_txt = self.small_font.render(f"🌟 BEST: {best_moves}", True, (220, 240, 180))  # Soft beige
                # Pixel-style outline for moves text
                for dx in [-1, 1]:
                    for dy in [-1, 1]:
                        outline_txt = self.small_font.render(f"🌟 BEST: {best_moves}", True, (80, 70, 60))
                        surf.blit(outline_txt, (rect.right - 30 - moves_txt.get_width() + dx, rect.top + 20 + dy))  # Same vertical alignment as title
                surf.blit(moves_txt, (rect.right - 30 - moves_txt.get_width(), rect.top + 20))
            else:
                # Show "Not Played" for unattempted levels
                placeholder_txt = self.status_font.render("❓ NOT PLAYED", True, (150, 170, 150))  # Pale green
                # Pixel-style outline for placeholder text
                for dx in [-1, 1]:
                    for dy in [-1, 1]:
                        outline_txt = self.status_font.render("❓ NOT PLAYED", True, (70, 80, 70))
                        surf.blit(outline_txt, (rect.right - 30 - placeholder_txt.get_width() + dx, rect.top + 20 + dy))  # Same vertical alignment as title
                surf.blit(placeholder_txt, (rect.right - 30 - placeholder_txt.get_width(), rect.top + 20))

            # Draw best stars centered below the text rows
            best_stars = self.progress["best_stars"].get(size_key, 0)
            # Position stars centered below the other text, with more vertical space
            star_center = (rect.centerx, rect.centery + 15)  # More vertical spacing
            self._draw_small_stars(surf, star_center, best_stars, is_hovered)

        # Styled back button matching the theme (pixel-style wooden button)
        pygame.draw.rect(surf, (100, 85, 60), self.back_rect)
        pygame.draw.rect(surf, (70, 55, 35), self.back_rect, 2)
        # Pixel-style corner details for back button
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.x, self.back_rect.y, 3, 2))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.x, self.back_rect.y, 2, 3))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.right - 3, self.back_rect.y, 3, 2))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.right - 2, self.back_rect.y, 2, 3))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.x, self.back_rect.bottom - 2, 3, 2))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.x, self.back_rect.bottom - 3, 2, 3))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.right - 3, self.back_rect.bottom - 2, 3, 2))
        pygame.draw.rect(surf, (70, 55, 35), (self.back_rect.right - 2, self.back_rect.bottom - 3, 2, 3))
        
        back_txt = self.small_font.render("BACK", True, (220, 240, 220))
        # Pixel-style outline for back button text
        for dx in [-1, 1]:
            for dy in [-1, 1]:
                outline_txt = self.small_font.render("BACK", True, (80, 70, 60))
                surf.blit(outline_txt, (self.back_rect.centerx - back_txt.get_width() // 2 + dx, 
                                      self.back_rect.centery - back_txt.get_height() // 2 + dy))
        surf.blit(back_txt, (self.back_rect.centerx - back_txt.get_width() // 2, 
                            self.back_rect.centery - back_txt.get_height() // 2))

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