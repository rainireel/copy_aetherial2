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
        title = self.title_font.render("Aetherial Gardens", True, (200, 230, 200))
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
        # Pause button (simple ► symbol)
        pygame.draw.rect(surf, (80, 100, 80), self.pause_rect, border_radius=5)
        pygame.draw.rect(surf, (30, 50, 30), self.pause_rect, 2, border_radius=5)
        pause_sym = self.font.render("II", True, (255, 255, 255))
        sym_rect = pause_sym.get_rect(center=self.pause_rect.center)
        surf.blit(pause_sym, sym_rect)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.pause_rect.collidepoint(event.pos):
                self.pause_cb()