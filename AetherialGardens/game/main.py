"""game/main.py – entry point for Aetherial Gardens (MVP skeleton).
Runs a simple 800×600 Pygame window with a dark‑green background.
"""

import sys
import pygame
from .puzzle import Board
from .ui import Menu, HUD

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
pygame.mixer.init()  # Initialize the mixer for audio
pygame.display.set_caption(WINDOW_TITLE)
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# ------------------------------------------------------------ 
# Load audio files if they exist
# ------------------------------------------------------------
try:
    move_sound = pygame.mixer.Sound("assets/audio/move.wav")
except pygame.error:
    move_sound = None  # No sound file available

try:
    pygame.mixer.music.load("assets/audio/ambient.mp3")
    pygame.mixer.music.play(-1)  # Loop indefinitely
except pygame.error:
    pass  # No music file available

# -----------------------------------------------------------------
# Game state flags
# -----------------------------------------------------------------
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"

# Main loop – keep the window responsive until the user closes it.
running = True
game_state = STATE_MENU

def start_game():
    global game_state, board, hud
    board = Board(rows=3, cols=3, tile_size=150, margin=5, move_sound=move_sound) # fresh scramble with sound
    hud.move_count = 0
    game_state = STATE_PLAYING

def quit_game():
    global running
    running = False

def toggle_pause():
    global game_state
    if game_state == STATE_PLAYING:
        game_state = STATE_PAUSED
    elif game_state == STATE_PAUSED:
        game_state = STATE_PLAYING

# -----------------------------------------------------------------
# Initialise objects that live across states
# -----------------------------------------------------------------
board = Board(rows=3, cols=3, tile_size=150, margin=5)
hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=toggle_pause)
menu = Menu(pygame.Rect(0, 0, *WINDOW_SIZE), start_cb=start_game, quit_cb=quit_game)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == STATE_MENU:
            menu.handle_event(event)
        elif game_state == STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                before = board.is_solved()
                board.click_at(event.pos)
                # Increment moves only if a tile actually moved
                if not before and not board.is_solved():
                    hud.increment_moves()
                hud.handle_event(event)
        elif game_state == STATE_PAUSED:
            hud.handle_event(event) # allow un‑pause via button

    # -----------------------------------------------------------------
    # Rendering – draw according to the current state
    # -----------------------------------------------------------------
    screen.fill(BG_COLOR)
    if game_state == STATE_MENU:
        menu.draw(screen)
    else:
        board.draw(screen, pygame.font.SysFont(None, 48))
        hud.draw(screen)
        if board.is_solved():
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg = pygame.font.SysFont(None, 72).render("Puzzle solved!", True, (255, 255, 255))
            rect = msg.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            screen.blit(msg, rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()