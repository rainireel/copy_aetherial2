"""game/main.py – entry point (now includes Level‑Select)."""

import sys
import pygame
from pathlib import Path

# -----------------------------------------------------------------
# Local imports
# -----------------------------------------------------------------
from .puzzle import Board
from .ui import Menu, HUD, LevelSelect
from .audio import init_mixer, load_sfx, load_music, play_move, start_ambient_loop
from .save import load_progress, save_progress
from .levels import LEVELS   # list of LevelInfo objects

# -----------------------------------------------------------------
# Constants
# -----------------------------------------------------------------
WINDOW_TITLE = "Aetherial"
WINDOW_SIZE = (800, 600)
BG_COLOR = (10, 30, 20)          # dark‑green fallback
FPS = 60

# -----------------------------------------------------------------
# pygame init
# -----------------------------------------------------------------
pygame.init()
pygame.display.set_caption(WINDOW_TITLE)
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# -----------------------------------------------------------------
# Audio init (must be after pygame.init)
# -----------------------------------------------------------------
init_mixer()
_move_sfx = load_sfx()
load_music()
start_ambient_loop()

# -----------------------------------------------------------------
# Load persisted progress (best moves per level)
# -----------------------------------------------------------------
progress = load_progress()   # dict stored in save_data.json

# -----------------------------------------------------------------
# Game‑state flags
# -----------------------------------------------------------------
STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"

game_state = STATE_MENU
selected_level = None   # will hold a LevelInfo once the player picks one
board = None            # created after a level is chosen

# -----------------------------------------------------------------
# UI objects (instantiated lazily because they need callbacks)
# -----------------------------------------------------------------
hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=lambda: toggle_pause())

def quit_game():
    """Signal the main loop to exit."""
    global running
    running = False

def back_to_menu():
    global game_state
    game_state = STATE_MENU

def start_game(level_info):
    """Callback from LevelSelect – build a Board of the chosen size."""
    global game_state, board, selected_level, hud
    selected_level = level_info
    board = Board(
        rows=level_info.rows,
        cols=level_info.rows,
        tile_size=120,
        margin=4,
    )
    hud.move_count = 0
    # Load any previously saved best for this size
    key = f"best_{level_info.rows}x{level_info.rows}"
    if key in progress and progress[key] is not None:
        hud.move_count = progress[key]   # just for display; not a record
    game_state = STATE_PLAYING

def toggle_pause():
    """Switch between playing and paused."""
    global game_state
    if game_state == STATE_PLAYING:
        game_state = STATE_PAUSED
    elif game_state == STATE_PAUSED:
        game_state = STATE_PLAYING

# -----------------------------------------------------------------
# Menus / screens
# -----------------------------------------------------------------
menu = Menu(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    start_cb=lambda: switch_state(STATE_LEVEL_SELECT),
    quit_cb=quit_game,
)

level_select = LevelSelect(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    start_cb=start_game,
    back_cb=back_to_menu,
)

def switch_state(new_state):
    """Utility to change the global state safely."""
    global game_state
    game_state = new_state

# -----------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == STATE_MENU:
            menu.handle_event(event)
        elif game_state == STATE_LEVEL_SELECT:
            level_select.handle_event(event)
        elif game_state == STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Record if a move actually occurred by checking board state before and after
                board_empty_pos_before = board.empty_pos
                board.click_at(event.pos)
                # If the empty position changed, a move occurred
                if board_empty_pos_before != board.empty_pos:
                    play_move()
                    hud.increment_moves()
            hud.handle_event(event)
        elif game_state == STATE_PAUSED:
            hud.handle_event(event)

    # ------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------
    screen.fill(BG_COLOR)

    if game_state == STATE_MENU:
        menu.draw(screen)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.draw(screen)
    else:   # STATE_PLAYING or STATE_PAUSED
        # Draw the level‑specific background (if it exists)
        if selected_level:
            try:
                bg_surf = pygame.image.load(str(selected_level.bg_path)).convert()
                # Scale the background image to fill the entire screen
                bg_surf = pygame.transform.scale(bg_surf, WINDOW_SIZE)
                screen.blit(bg_surf, (0, 0))
            except Exception:
                # fallback to plain BG_COLOR if image fails
                screen.fill(BG_COLOR)
        else:
            screen.fill(BG_COLOR)

        board.draw(screen, pygame.font.SysFont(None, 48))
        hud.draw(screen)

        if board.is_solved():
            # Record best moves for this board size
            key = f"best_{selected_level.rows}x{selected_level.rows}"
            if (progress.get(key) is None) or (hud.move_count < progress[key]):
                progress[key] = hud.move_count

            # Simple “solved” overlay
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg = pygame.font.SysFont(None, 72).render("Puzzle solved!", True, (255, 255, 255))
            rect = msg.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            screen.blit(msg, rect)

    pygame.display.flip()
    clock.tick(FPS)

# ------------------------------------------------------------
# Save progress before exiting (best‑move data)
# ------------------------------------------------------------
save_progress(progress)
pygame.quit()
sys.exit()