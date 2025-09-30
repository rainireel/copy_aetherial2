"""game/main.py – entry point for Aetherial Gardens (MVP skeleton).
Runs a simple 800×600 Pygame window with a dark‑green background.
"""

import sys
import pygame
from puzzle import Board

# ------------------------------------------------------------
# Constants (easy to tweak later)
# ------------------------------------------------------------
WINDOW_TITLE = "Aetherial Gardens – Shard of Memory"
WINDOW_SIZE = (800, 600)
BG_COLOR = (10, 30, 20) # very dark green, calming
FPS = 60

# ------------------------------------------------------------
# initialise pygame – must happen before any font, mixer, or surface use
# ------------------------------------------------------------
pygame.init()
pygame.display.set_caption(WINDOW_TITLE)
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# -----------------------------------------------------------------
# Initialise board (3×3) – can be tweaked later via Board(rows, cols)
# -----------------------------------------------------------------
board = Board(rows=3, cols=3, tile_size=150, margin=5)

# Main loop – keep the window responsive until the user closes it.
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            board.click_at(event.pos)

    # Clear screen and draw the puzzle board
    screen.fill(BG_COLOR)
    board.draw(screen, pygame.font.SysFont(None, 48))

    # Show a simple overlay when the puzzle is solved
    if board.is_solved():
        overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        congrats = pygame.font.SysFont(None, 72).render("Puzzle solved!", True, (255, 255, 255))
        rect = congrats.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
        screen.blit(congrats, rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()