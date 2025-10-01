"""game/main.py – entry point (now with a Settings screen)."""

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
    play,
    set_volume,                # <-- NEW
)
from .save import load_progress, save_progress, star_key
from .star import StarHUD
from .pause import PauseMenu
from .settings import SettingsScreen   # <-- NEW

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
_move_sfx = load_sfx()          # populates the internal _sounds dict
load_music()
start_ambient_loop()

# -----------------------------------------------------------------
# Load persisted progress (now includes volume & mute)
# -----------------------------------------------------------------
progress = load_progress()
# Apply saved volume / mute on start‑up
if progress.get("muted", False):
    set_volume(0.0)
else:
    set_volume(progress.get("volume", 0.4))

# -----------------------------------------------------------------
# Game‑state flags
# -----------------------------------------------------------------
STATE_MENU = "menu"
STATE_LEVEL_SELECT = "level_select"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_SETTINGS = "settings"      # ★‑Settings addition

game_state = STATE_MENU
selected_level = None
board = None

# -----------------------------------------------------------------
# Screen transition variables
# -----------------------------------------------------------------
transition_alpha = 255  # Start with no transition (fully visible)
in_transition = False   # Whether a transition is currently happening
transition_duration = 500  # Duration of transition in milliseconds
transition_start_time = 0

# -----------------------------------------------------------------
# UI objects
# -----------------------------------------------------------------
hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=lambda: toggle_pause())
star_hud = StarHUD(pygame.Rect(0, 0, *WINDOW_SIZE))

def quit_game():
    global running
    running = False

def back_to_menu():
    switch_state(STATE_MENU)

def restart_current_level():
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
    if "best_moves" in progress and key in progress["best_moves"]:
        hud.move_count = progress["best_moves"][key]
    game_state = STATE_PLAYING
    star_hud.set_rating(0)

def toggle_pause():
    global game_state
    if game_state == STATE_PLAYING:
        switch_state(STATE_PAUSED)
    elif game_state == STATE_PAUSED:
        switch_state(STATE_PLAYING)

# -----------------------------------------------------------------
# Settings screen (volume slider + mute)
# -----------------------------------------------------------------
def get_volume() -> float:
    return 0.0 if progress.get("muted", False) else progress.get("volume", 0.4)

def set_volume_callback(level: float) -> None:
    # Store the new volume (but keep muted flag unchanged)
    progress.setdefault("volume", 0.4)
    progress["volume"] = level
    if not progress.get("muted", False):
        set_volume(level)          # apply immediately
    save_progress(progress)

def toggle_mute() -> None:
    muted = not progress.get("muted", False)
    progress.setdefault("muted", False)
    progress["muted"] = muted
    set_volume(0.0 if muted else progress.get("volume", 0.4))
    save_progress(progress)

settings_screen = SettingsScreen(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    get_volume=get_volume,
    set_volume=set_volume_callback,
    get_muted=lambda: progress.get("muted", False),
    set_muted=lambda val: toggle_mute(),
    back_cb=lambda: switch_state(STATE_MENU),
)

# -----------------------------------------------------------------
# Menus / screens
# -----------------------------------------------------------------
menu = Menu(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    start_cb=lambda: switch_state(STATE_LEVEL_SELECT),
    settings_cb=lambda: switch_state(STATE_SETTINGS),   # ★‑Settings addition
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

def start_transition():
    """Start a fade transition."""
    global in_transition, transition_alpha, transition_start_time
    in_transition = True
    transition_alpha = 0  # Start fully transparent
    transition_start_time = pygame.time.get_ticks()

def finish_transition():
    """Complete the transition and update game state."""
    global in_transition, transition_alpha, game_state
    in_transition = False
    transition_alpha = 0

# Global variable for transition target state
target_state = None

def switch_state(new_state):
    global target_state
    start_transition()
    # For this implementation, we'll handle the actual state change after the transition
    target_state = new_state

def apply_state_change():
    """Actually apply the state change after transition."""
    global game_state, target_state
    if target_state is not None:
        game_state = target_state
        target_state = None

# -----------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------
running = True
while running:
    # Calculate delta time for animations
    dt = clock.tick(FPS)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == STATE_MENU:
            menu.handle_event(event)
        elif game_state == STATE_LEVEL_SELECT:
            level_select.handle_event(event)
        elif game_state == STATE_SETTINGS:
            settings_screen.handle_event(event)
        elif game_state == STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Store original empty position to compare later
                original_empty_pos = board.empty_pos
                
                # Process the click
                board.click_at(event.pos)
                
                # If the empty position changed, it means a tile was moved
                if board.empty_pos != original_empty_pos:
                    # A valid move was made
                    hud.increment_moves()
                    play_move()
                    play("place")
            hud.handle_event(event)
        elif game_state == STATE_PAUSED:
            pause_menu.handle_event(event)
            hud.handle_event(event)

    # Update UI components for animations
    if game_state == STATE_MENU:
        menu.update(dt)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.update(dt)
    elif game_state == STATE_SETTINGS:
        settings_screen.update(dt)
    elif game_state == STATE_PLAYING or game_state == STATE_PAUSED:
        # Update HUD even when playing
        pass  # HUD doesn't currently have animations

    # Handle screen transitions
    if in_transition:
        elapsed = pygame.time.get_ticks() - transition_start_time
        transition_progress = min(elapsed / transition_duration, 1.0)
        
        # Fade in: alpha goes from 0 to 255
        transition_alpha = int(transition_progress * 255)
        
        if transition_progress >= 1.0:
            finish_transition()
            apply_state_change()

    # ------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------
    screen.fill(BG_COLOR)

    if game_state == STATE_MENU:
        menu.draw(screen)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.draw(screen)
    elif game_state == STATE_SETTINGS:
        settings_screen.draw(screen)
    else:   # PLAYING or PAUSED
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

        if board.is_solved():
            rating = StarHUD.compute_rating(selected_level.rows, hud.move_count)
            star_hud.set_rating(rating)

            size_key = star_key(selected_level.rows)

            # Best‑move logic
            best_moves = progress.get("best_moves", {}).get(size_key)
            if best_moves is None or hud.move_count < best_moves:
                progress.setdefault("best_moves", {})[size_key] = hud.move_count

            # Best‑star logic
            best_star = progress.get("best_stars", {}).get(size_key, 0)
            if rating > best_star:
                progress.setdefault("best_stars", {})[size_key] = rating

            play("complete")   # ★‑SFX for puzzle solved

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

    # Draw transition overlay if in transition
    if in_transition:
        transition_overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
        transition_overlay.fill((0, 0, 0, transition_alpha))
        screen.blit(transition_overlay, (0, 0))

    pygame.display.flip()

# ------------------------------------------------------------
# Save progress before exiting (volume, mute, best moves, stars)
# ------------------------------------------------------------
save_progress(progress)
pygame.quit()
sys.exit()