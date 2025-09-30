"""game/main.py – entry point (now with star‑rating system)."""

import sys
import pygame
from pathlib import Path

# -----------------------------------------------------------------
# Local imports
# -----------------------------------------------------------------
from .puzzle import Board
from .ui import Menu, HUD, LevelSelect
from .audio import init_mixer, load_sfx, load_music, play_move, start_ambient_loop
from .save import load_progress, save_progress, star_key
from .star import StarHUD
from .pause import PauseMenu

# -----------------------------------------------------------------
# Constants
# -----------------------------------------------------------------
WINDOW_TITLE = "Aetherial Gardens – Shard of Memory"
WINDOW_SIZE = (800, 600)
BG_COLOR = (10, 30, 20)          # fallback background colour
FPS = 60

# -----------------------------------------------------------------
# pygame init
# -----------------------------------------------------------------
pygame.init()
pygame.display.set_caption(WINDOW_TITLE)
screen = pygame.display.set_mode(WINDOW_SIZE)
clock = pygame.time.Clock()

# -----------------------------------------------------------------
# Audio init
# -----------------------------------------------------------------
init_mixer()
_move_sfx = load_sfx()
load_music()
start_ambient_loop()

# -----------------------------------------------------------------
# Load persisted progress (best moves + best stars per board size)
# -----------------------------------------------------------------
progress = load_progress()   # {"best_moves": {...}, "best_stars": {...}}

# -----------------------------------------------------------------
# Game‑state flags
# -----------------------------------------------------------------
STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"

game_state = STATE_MENU
selected_level = None   # will hold a LevelInfo once chosen
board = None            # created after level selection

# -----------------------------------------------------------------
# UI objects (instantiated lazily because they need callbacks)
# -----------------------------------------------------------------
hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=lambda: toggle_pause())
star_hud = StarHUD(pygame.Rect(0, 0, *WINDOW_SIZE))

def quit_game():
    """Signal the main loop to exit."""
    global running
    running = False

def back_to_menu():
    """Return from Level‑Select (or from pause) to the Main Menu."""
    global game_state
    game_state = STATE_MENU

def start_game(level_info):
    """Callback from LevelSelect – build a Board of the chosen size."""
    global game_state, board, selected_level, hud, star_hud
    selected_level = level_info
    board = Board(
        rows=level_info.rows,
        cols=level_info.rows,
        tile_size=120,
        margin=4,
    )
    hud.move_count = 0
    # Load any saved best‑move count for display (not a record yet)
    key = star_key(level_info.rows)
    if key in progress["best_moves"]:
        hud.move_count = progress["best_moves"][key]
    game_state = STATE_PLAYING
    star_hud.set_rating(0)   # clear any old stars

def toggle_pause():
    """Switch between playing and paused."""
    global game_state
    if game_state == STATE_PLAYING:
        game_state = STATE_PAUSED
    elif game_state == STATE_PAUSED:
        game_state = STATE_PLAYING

def resume_game():
    """Resume gameplay from pause menu."""
    global game_state
    game_state = STATE_PLAYING

def restart_level():
    """Restart the current level with a new scrambled board."""
    global board, hud, game_state, star_hud
    if selected_level:
        # Create a new board with the same settings
        board = Board(
            rows=selected_level.rows,
            cols=selected_level.rows,
            tile_size=120,
            margin=4,
        )
        # Reset move counter
        hud.move_count = 0
        # Reset star rating display
        star_hud.set_rating(0)
        # Return to playing state
        game_state = STATE_PLAYING

def return_to_main_menu():
    """Return to the main menu from pause menu."""
    global game_state
    game_state = STATE_MENU

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

# Initialize the pause menu with callback functions
pause_menu = PauseMenu(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    resume_cb=resume_game,
    restart_cb=restart_level,
    main_menu_cb=return_to_main_menu,
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
            pause_menu.handle_event(event)

    # ------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------
    screen.fill(BG_COLOR)

    if game_state == STATE_MENU:
        menu.draw(screen)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.draw(screen)
    else:  # PLAYING or PAUSED
        # Draw garden background if a level is selected
        if selected_level:
            try:
                bg = pygame.image.load(str(selected_level.bg_path)).convert()
                # Scale the background image to fill the entire screen
                bg = pygame.transform.scale(bg, WINDOW_SIZE)
                screen.blit(bg, (0, 0))
            except Exception:
                screen.fill(BG_COLOR)   # fallback
        else:
            screen.fill(BG_COLOR)

        board.draw(screen, pygame.font.SysFont(None, 48))
        hud.draw(screen)

        # --------------------------------------------------------
        # ★‑rating – compute & display when the puzzle is solved
        # --------------------------------------------------------
        if board.is_solved():
            # Compute the star rating for this board size
            rating = StarHUD.compute_rating(selected_level.rows, hud.move_count)
            star_hud.set_rating(rating)

            # Persist best moves & best stars (if this run is better)
            size_key = star_key(selected_level.rows)

            # Best‑move logic (same as before)
            best_moves = progress["best_moves"].get(size_key)
            if best_moves is None or hud.move_count < best_moves:
                progress["best_moves"][size_key] = hud.move_count

            # Best‑star logic
            best_star = progress["best_stars"].get(size_key, 0)
            if rating > best_star:
                progress["best_stars"][size_key] = rating

            # Solved overlay
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg = pygame.font.SysFont(None, 72).render("Puzzle solved!", True, (255, 255, 255))
            rect = msg.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            screen.blit(msg, rect)

        # Draw the star HUD (always visible – shows 0 stars until solved)
        star_hud.draw(screen)

        # --------------------------------------------------------
        # Pause menu (shows when game is paused)
        # --------------------------------------------------------
        if game_state == STATE_PAUSED:
            pause_menu.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

# ------------------------------------------------------------
# Save progress before exiting (best moves + best stars)
# ------------------------------------------------------------
save_progress(progress)
pygame.quit()
sys.exit()