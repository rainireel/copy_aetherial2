"""game/ui.py – tiny UI helpers for the MVP.
Only pygame is used; everything stays under 150 lines.
"""


import pygame
from typing import Callable, Tuple

# Import the audio system for UI sounds
from .audio import play

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
                play('ui')  # Play UI click sound
                self.callback()

# ------------------------------------------------------------
# Menu – collection of Buttons shown before the game starts.
# ------------------------------------------------------------
class Menu:
    def __init__(self, screen_rect: pygame.Rect, start_cb: Callable[[], None], settings_cb: Callable[[], None], quit_cb: Callable[[], None]):
        w, h = screen_rect.size
        btn_w, btn_h = 250, 60
        spacing = 20
        center_x = w // 2
        start_rect = pygame.Rect(0, 0, btn_w, btn_h)
        start_rect.center = (center_x, h // 2 - spacing * 2)  # Adjust position for 3 buttons
        settings_rect = pygame.Rect(0, 0, btn_w, btn_h)
        settings_rect.center = (center_x, h // 2)            # Middle button
        quit_rect = pygame.Rect(0, 0, btn_w, btn_h)
        quit_rect.center = (center_x, h // 2 + spacing * 2)   # Bottom button
        self.buttons = [
            Button(start_rect, "Start", start_cb),
            Button(settings_rect, "Settings", settings_cb),  # Add settings button
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
        # Cozy garden-fantasy pixel fonts
        self.font = pygame.font.SysFont('Arial', 26, bold=True)  # More readable font
        self.title_font = pygame.font.SysFont('Arial', 36, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 20)  # Larger for better readability
        self.status_font = pygame.font.SysFont('Arial', 18, bold=True)  # For status text

        # Button geometry – resized to better fit content
        btn_w, btn_h = 320, 85  # Smaller height to match content
        spacing = 30  # Consistent spacing between buttons
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
    # Helper: draw cozy garden-style small stars with animation
    # -----------------------------------------------------------------
    def _draw_small_stars(self, surf: pygame.Surface, center: tuple[int, int], rating: int, is_hovered=False):
        """Draw 0‑3 gold stars in cozy garden style."""
        star_size = 12  # Larger for better readability
        spacing = 8  # Better spacing between stars
        
        for i in range(rating):
            # Calculate x position for each star
            total_width = rating * star_size + (rating - 1) * spacing
            start_x = center[0] - total_width // 2
            
            star_x = start_x + i * (star_size + spacing)
            star_y = center[1] - star_size // 2
            
            # Draw a cozy garden-style star (more clearly defined)
            star_color = (255, 215, 0)  # Gold color
            if is_hovered:
                # Brighten hover effect
                star_color = (255, 230, 100)
            
            # Draw a simple 5-pointed star using polygon
            points = []
            for j in range(10):
                angle = j * 36
                radius = star_size // 2 if j % 2 == 0 else star_size // 4
                rad = pygame.math.Vector2(1, 0).rotate(angle) * radius
                points.append((star_x + star_size // 2 + int(rad.x), 
                              star_y + star_size // 2 + int(rad.y)))
            
            pygame.draw.polygon(surf, star_color, points)

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
        # Cozy garden-themed background
        overlay = pygame.Surface(surf.get_size())
        overlay.fill((10, 40, 20))  # Dark green background
        # Add subtle organic grid pattern for garden feel
        for y in range(0, surf.get_height(), 16):
            for x in range(0, surf.get_width(), 16):
                if (x // 16 + y // 16) % 3 == 0:
                    pygame.draw.rect(overlay, (8, 35, 18), (x, y, 8, 8))
        surf.blit(overlay, (0, 0))

        # Title with cozy garden fantasy theme
        title = self.title_font.render("AETHERIAL GARDENS", True, (180, 230, 150))  # Pastel green
        title_rect = title.get_rect(center=(surf.get_width() // 2, 80))
        
        # Softer glow effect for garden fantasy feel
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:  # Skip the center
                    outline = self.title_font.render("AETHERIAL GARDENS", True, (60, 100, 70))
                    surf.blit(outline, (title_rect.x + dx, title_rect.y + dy))
        
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
            
            # Button background with cozy garden frame
            bg_color = (135, 115, 85) if is_hovered else (120, 100, 75)  # Warm brown tones
            border_color = (85, 65, 45) if not is_hovered else (145, 125, 100)
            
            # Draw cozy garden button with consistent 12px padding
            pygame.draw.rect(surf, bg_color, rect)
            # Inner padding area
            inner_rect = pygame.Rect(rect.x + 12, rect.y + 12, rect.width - 24, rect.height - 24)
            pygame.draw.rect(surf, (140, 120, 95), inner_rect)
            
            # Draw frame with consistent styling
            pygame.draw.rect(surf, border_color, rect, 2)

            # Row 1: Title with difficulty icon
            txt = self.font.render(lvl.name, True, (240, 250, 210))  # Light cream
            # Draw difficulty icon first (like 🌱, 🌿, 🌳)
            icon_width = 20
            icon_x = rect.left + 15
            icon_y = rect.top + 18  # Consistent vertical alignment
            self._draw_difficulty_icon(surf, (icon_x, icon_y), lvl.rows)
            
            # Text next to icon with consistent spacing
            text_x = icon_x + icon_width + 8  # 8px spacing between icon and text
            text_y = rect.top + 15  # Top padding
            surf.blit(txt, (text_x, text_y))

            # Row 2: Status with star icon
            size_key = self.star_key(lvl.rows)
            best_moves = self.progress["best_moves"].get(size_key)
            
            if best_moves is not None:
                # Status text with star icon - second row below title
                status_txt = self.small_font.render(f"🌟 BEST: {best_moves}", True, (220, 240, 190))  # Light beige
                status_x = rect.left + 15  # Left align with the icon above
                status_y = rect.top + 45  # Second row, below the title row
                surf.blit(status_txt, (status_x, status_y))
            else:
                # Show "Not Played" for unattempted levels
                status_txt = self.status_font.render("❓ NOT PLAYED", True, (160, 180, 160))  # Muted green
                status_x = rect.left + 15  # Left align with the icon above
                status_y = rect.top + 45  # Second row, below the title row
                surf.blit(status_txt, (status_x, status_y))

            # Draw best stars centered below both rows
            best_stars = self.progress["best_stars"].get(size_key, 0)
            # Position stars centered below the text with proper spacing
            star_center = (rect.centerx, rect.top + 70)  # Below both text rows
            self._draw_small_stars(surf, star_center, best_stars, is_hovered)

        # Styled back button
        pygame.draw.rect(surf, (120, 100, 75), self.back_rect)
        pygame.draw.rect(surf, (85, 65, 45), self.back_rect, 2)
        
        back_txt = self.small_font.render("BACK", True, (220, 240, 220))
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