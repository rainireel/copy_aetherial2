"""game/settings.py – simple volume / mute UI.

The screen draws a semi‑transparent overlay with:
* a horizontal slider (0 % – 100 % volume)
* a mute / un‑mute toggle button
* a "Back" button to return to the previous state.
"""

import pygame
from typing import Callable, Tuple

class SettingsScreen:
    """UI that lets the player adjust audio volume and mute."""
    def __init__(
        self,
        screen_rect: pygame.Rect,
        get_volume: Callable[[], float],
        set_volume: Callable[[float], None],
        get_muted: Callable[[], bool],
        set_muted: Callable[[bool], None],
        back_cb: Callable[[], None],
    ):
        self.rect = screen_rect
        self.get_volume = get_volume
        self.set_volume = set_volume
        self.get_muted = get_muted
        self.set_muted = set_muted
        self.back_cb = back_cb

        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)

        # Slider geometry
        self.slider_rect = pygame.Rect(
            screen_rect.centerx - 150, screen_rect.centery - 20, 300, 8
        )
        self.knob_radius = 12
        self.dragging = False

        # Mute toggle button (small square)
        self.mute_rect = pygame.Rect(
            screen_rect.centerx - 30, self.slider_rect.bottom + 40, 60, 30
        )

        # Back button (bottom‑left)
        self.back_rect = pygame.Rect(10, screen_rect.height - 50, 80, 35)

    # -----------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------
    def draw(self, surf: pygame.Surface) -> None:
        # Dim the whole screen
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surf.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("Settings", True, (230, 230, 230))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.top + 70))
        surf.blit(title, title_rect)

        # Volume label
        vol_label = self.font.render("Volume", True, (200, 200, 200))
        vol_rect = vol_label.get_rect(midright=(self.slider_rect.left - 10, self.slider_rect.centery))
        surf.blit(vol_label, vol_rect)

        # Slider line
        pygame.draw.rect(surf, (150, 150, 150), self.slider_rect, border_radius=4)

        # Knob (position reflects current volume)
        vol = self.get_volume()   # 0.0 – 1.0
        knob_x = self.slider_rect.left + int(vol * self.slider_rect.width)
        knob_center = (knob_x, self.slider_rect.centery)
        pygame.draw.circle(surf, (255, 215, 0), knob_center, self.knob_radius)
        pygame.draw.circle(surf, (30, 30, 30), knob_center, self.knob_radius, 2)

        # Mute button
        mute_txt = "Un‑mute" if self.get_muted() else "Mute"
        pygame.draw.rect(surf, (80, 80, 120), self.mute_rect, border_radius=5)
        pygame.draw.rect(surf, (30, 30, 60), self.mute_rect, 2, border_radius=5)
        mute_label = self.font.render(mute_txt, True, (255, 255, 255))
        mute_label_rect = mute_label.get_rect(center=self.mute_rect.center)
        surf.blit(mute_label, mute_label_rect)

        # Back button
        pygame.draw.rect(surf, (70, 90, 70), self.back_rect, border_radius=5)
        pygame.draw.rect(surf, (30, 50, 30), self.back_rect, 2, border_radius=5)
        back_label = self.font.render("Back", True, (255, 255, 255))
        back_rect = back_label.get_rect(center=self.back_rect.center)
        surf.blit(back_label, back_rect)

    # -----------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.slider_rect.collidepoint(event.pos):
                self.dragging = True
                self._set_volume_from_mouse(event.pos)
                return
            if self.mute_rect.collidepoint(event.pos):
                # Toggle mute flag
                self.set_muted(not self.get_muted())
                return
            if self.back_rect.collidepoint(event.pos):
                self.back_cb()
                return

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self._set_volume_from_mouse(event.pos)

    # -----------------------------------------------------------------
    def _set_volume_from_mouse(self, pos: Tuple[int, int]) -> None:
        """Convert the mouse x‑position into a 0‑1 volume level."""
        x = max(self.slider_rect.left, min(pos[0], self.slider_rect.right))
        rel = (x - self.slider_rect.left) / self.slider_rect.width
        # When muted, we still update the stored volume; the mute flag stays unchanged.
        self.set_volume(rel)