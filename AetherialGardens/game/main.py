"""game/main.py – entry point (now with extra SFX and settings)."""

import sys
import pygame
from pathlib import Path

# -----------------------------------------------------------------
# Local imports
# -----------------------------------------------------------------
from .puzzle import Board
from .ui import Menu, HUD, LevelSelect
from .audio import (
    init_mixer,
    load_sfx,
    load_music,
    play_move,
    start_ambient_loop,
    play,                     # <-- NEW
    set_volume,                # <-- NEW
)
from .save import load_progress, save_progress, star_key
from .star import StarHUD
from .pause import PauseMenu
from .settings import SettingsScreen           # <-- NEW

# -----------------------------------------------------------------
# Constants
# -----------------------------------------------------------------
WINDOW_TITLE = "Aetherial Gardens – Shard of Memory"
WINDOW_SIZE = (800, 600)
BG_COLOR = (10, 30, 20)
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
_move_sfx = load_sfx()          # populates the _sounds dict
load_music()
start_ambient_loop()

# -----------------------------------------------------------------
# Load persisted progress (best moves + best stars per board size + audio settings)
# -----------------------------------------------------------------
progress = load_progress()

# Apply initial audio settings from save file
set_volume(progress.get("volume", 0.4))
if progress.get("muted", False):
    pygame.mixer.music.set_volume(0)  # Mute if needed
    # Note: Individual SFX muting would need additional implementation

# -----------------------------------------------------------------
# UI objects (settings screen needs to be initialized after progress is loaded)
# -----------------------------------------------------------------
hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=lambda: toggle_pause())
star_hud = StarHUD(pygame.Rect(0, 0, *WINDOW_SIZE))

# Define callbacks for settings changes
def on_volume_change(vol: float) -> None:
    """Called when volume is changed in settings."""
    set_volume(vol)  # Update actual audio volume
    progress["volume"] = vol  # Update progress data

def on_mute_change(muted: bool) -> None:
    """Called when mute is changed in settings."""
    if muted:
        set_volume(0.0)  # Mute
    else:
        set_volume(progress.get("volume", 0.4))  # Restore volume
    progress["muted"] = muted  # Update progress data

settings_screen = SettingsScreen(
    pygame.Rect(0, 0, *WINDOW_SIZE), 
    back_cb=lambda: switch_state(STATE_MENU),
    volume_change_cb=on_volume_change,
    mute_change_cb=on_mute_change
)  # <-- NEW
# Initialize settings screen with saved values
settings_screen.set_volume(progress.get("volume", 0.4))
settings_screen.set_muted(progress.get("muted", False))

# -----------------------------------------------------------------
# Game‑state flags
# -----------------------------------------------------------------
STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_SETTINGS = "settings"         # <-- NEW

game_state = STATE_MENU
selected_level = None
board = None

# -----------------------------------------------------------------
# UI objects
# -----------------------------------------------------------------
hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=lambda: toggle_pause())
star_hud = StarHUD(pygame.Rect(0, 0, *WINDOW_SIZE))
# settings_screen is initialized after loading progress, so it can be set with the saved values

def quit_game():
    global running
    running = False

def back_to_menu():
    global game_state
    game_state = STATE_MENU

def restart_current_level():
    """Scramble the current board again and reset HUD."""
    global board, hud, star_hud
    if selected_level:
        board = Board(
            rows=selected_level.rows,
            cols=selected_level.rows,
            tile_size=120,
            margin=4,
        )
        hud.move_count = 0
        star_hud.set_rating(0)

def start_game(level_info):
    global game_state, board, selected_level, hud, star_hud
    selected_level = level_info
    board = Board(
        rows=level_info.rows,
        cols=level_info.rows,
        tile_size=120,
        margin=4,
    )
    hud.move_count = 0
    key = star_key(level_info.rows)
    if key in progress["best_moves"]:
        hud.move_count = progress["best_moves"][key]
    game_state = STATE_PLAYING
    star_hud.set_rating(0)

def toggle_pause():
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
    settings_cb=lambda: switch_state(STATE_SETTINGS),  # <-- NEW
    quit_cb=quit_game,
)

level_select = LevelSelect(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    start_cb=start_game,
    back_cb=back_to_menu,
)

pause_menu = PauseMenu(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    resume_cb=lambda: toggle_pause(),
    restart_cb=restart_current_level,
    main_menu_cb=back_to_menu,
)

def switch_state(new_state):
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
        elif game_state == STATE_SETTINGS:           # <-- NEW
            settings_screen.handle_event(event)     # <-- NEW
        elif game_state == STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Check if a valid move is about to be made before incrementing
                # We need to somehow detect if the board state changed
                # Store original empty position to compare later
                original_empty_pos = board.empty_pos
                
                # Process the click
                board.click_at(event.pos)
                
                # If the empty position changed, it means a tile was moved
                if board.empty_pos != original_empty_pos:
                    # A valid move was made
                    hud.increment_moves()
                    # Play both sounds when a tile is moved
                    play_move()          # legacy generic slide sound
                    play("place")        # new "correct placement" sound
            hud.handle_event(event)
        elif game_state == STATE_PAUSED:
            pause_menu.handle_event(event)
            hud.handle_event(event)

    # ------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------
    screen.fill(BG_COLOR)

    if game_state == STATE_MENU:
        menu.draw(screen)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.draw(screen)
    elif game_state == STATE_SETTINGS:              # <-- NEW
        settings_screen.draw(screen)               # <-- NEW
    else:  # PLAYING or PAUSED
        if selected_level:
            try:
                bg = pygame.image.load(str(selected_level.bg_path)).convert()
                # Scale the background image to fit the entire screen
                bg = pygame.transform.scale(bg, WINDOW_SIZE)
                screen.blit(bg, (0, 0))
            except Exception:
                screen.fill(BG_COLOR)
        else:
            screen.fill(BG_COLOR)

        board.draw(screen, pygame.font.SysFont(None, 48))
        hud.draw(screen)

        # --------------------------------------------------------
        # ★‑rating – compute & display when solved (unchanged)
        # --------------------------------------------------------
        if board.is_solved():
            rating = StarHUD.compute_rating(selected_level.rows, hud.move_count)
            star_hud.set_rating(rating)

            size_key = star_key(selected_level.rows)

            # Best-move logic (same as before)
            best_moves = progress["best_moves"].get(size_key)
            if best_moves is None or hud.move_count < best_moves:
                progress["best_moves"][size_key] = hud.move_count

            # Best-star logic
            best_star = progress["best_stars"].get(size_key, 0)
            if rating > best_star:
                progress["best_stars"][size_key] = rating

            # ----- puzzle‑complete chime ----- #
            play("complete")   # ★‑SFX addition

            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            msg = pygame.font.SysFont(None, 72).render(
                "Puzzle solved!", True, (255, 255, 255)
            )
            rect = msg.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            screen.blit(msg, rect)

        star_hud.draw(screen)

        if game_state == STATE_PAUSED:
            pause_menu.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

# ------------------------------------------------------------
# Save progress before exiting
# ------------------------------------------------------------
save_progress(progress)
pygame.quit()
sys.exit()