"""game/pause.py – simple pause overlay with a mini‑menu.

The menu appears on top of the current board (dimmed background) and
offers three actions:
    • Resume – returns to gameplay
    • Restart – scrambles the current board again, resetting the move counter
    • Main Menu – goes back to the title screen

All drawing is done with pygame primitives; no external assets required.
"""

import pygame
from typing import Callable, Tuple


class PauseMenu:
    """Overlay that captures input while the game is paused."""

    def __init__(
        self,
        screen_rect: pygame.Rect,
        resume_cb: Callable[[], None],
        restart_cb: Callable[[], None],
        main_menu_cb: Callable[[], None],
    ):
        self.rect = screen_rect
        self.resume_cb = resume_cb
        self.restart_cb = restart_cb
        self.main_menu_cb = main_menu_cb
        self.font = pygame.font.SysFont(None, 48)

        # Build three centered buttons (same size, vertical stack)
        btn_w, btn_h = 250, 70
        spacing = 20
        total_h = 3 * btn_h + 2 * spacing
        start_y = (self.rect.height - total_h) // 2
        cx = self.rect.centerx

        self.buttons: list[tuple[pygame.Rect, str, Callable[[], None]]] = []

        for idx, (label, cb) in enumerate(
            [
                ("Resume", self.resume_cb),
                ("Restart", self.restart_cb),
                ("Main Menu", self.main_menu_cb),
            ]
        ):
            r = pygame.Rect(0, 0, btn_w, btn_h)
            r.centerx = cx
            r.y = start_y + idx * (btn_h + spacing)
            self.buttons.append((r, label, cb))

    # -----------------------------------------------------------------
    # Rendering
    # -----------------------------------------------------------------
    def draw(self, surf: pygame.Surface) -> None:
        # Dim the whole screen
        overlay = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))

        # Title text
        title = self.font.render("Paused", True, (220, 220, 220))
        title_rect = title.get_rect(center=(self.rect.centerx, self.rect.top + 80))
        surf.blit(title, title_rect)

        # Buttons
        for rect, label, _ in self.buttons:
            pygame.draw.rect(surf, (70, 120, 90), rect, border_radius=8)
            pygame.draw.rect(surf, (30, 60, 45), rect, 2, border_radius=8)
            txt = self.font.render(label, True, (255, 255, 255))
            txt_rect = txt.get_rect(center=rect.center)
            surf.blit(txt, txt_rect)

    # -----------------------------------------------------------------
    # Event handling
    # -----------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for rect, _, cb in self.buttons:
            if rect.collidepoint(event.pos):
                cb()
                return