"""game/main.py – entry point (now with a Settings screen)."""

import sys
import pygame
from pathlib import Path

# -----------------------------------------------------------------
# Local imports
# -----------------------------------------------------------------
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from puzzle import Board
from ui import Menu, HUD, LevelSelect, Button, Guide
from audio import (
    init_mixer,
    load_sfx,
    load_music,
    play_move,
    start_ambient_loop,
    play,
    set_volume,                # <-- NEW
)
from save import load_progress, save_progress
from star import StarHUD
from pause import PauseMenu
from settings import SettingsScreen   # <-- NEW
from image_loader import ImageLoader
from custom_puzzle import CustomPuzzleScreen
from cropping_tool import CroppingTool
from gallery import Gallery, GalleryScreen  # <-- NEW
from win_screen import WinScreen  # Win/restoration screen
from celebration import CelebrationOverlay  # Celebration overlay for solved puzzles

# -----------------------------------------------------------------
# Constants
# -----------------------------------------------------------------
WINDOW_TITLE = "Aetherial Levels – Shard of Memory"
WINDOW_SIZE = (1280, 720)
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
# Custom puzzle initialization happens after UI objects are created
# -----------------------------------------------------------------

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
STATE_CUSTOM_PUZZLE = "custom_puzzle"
STATE_CROPPING = "cropping"
STATE_GALLERY = "gallery"  # <-- NEW
STATE_GUIDE = "guide"
STATE_WIN = "win"  # Win/restoration screen

game_state = STATE_MENU
selected_level = None
board = None
custom_puzzle_screen = None
cropping_tool = None
gallery_screen = None  # <-- NEW
just_saved_to_gallery = False  # <-- NEW: Track if we just saved to gallery
win_screen = None  # Win screen instance
celebration_overlay = None  # Celebration overlay instance
puzzle_solved_celebrated = False  # Flag to prevent re-triggering celebration
win_screen_initiated = False # Flag to prevent re-triggering win screen

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
def show_guide():
    switch_state(STATE_GUIDE)

def hide_guide():
    switch_state(STATE_PLAYING)

hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=lambda: toggle_pause(), guide_cb=show_guide)
guide = Guide(pygame.Rect(0, 0, *WINDOW_SIZE), close_cb=hide_guide)
star_hud = StarHUD(pygame.Rect(0, 0, *WINDOW_SIZE))

def quit_game():
    global running
    running = False

def back_to_menu():
    switch_state(STATE_MENU)

def restart_current_level():
    global board, hud, star_hud, puzzle_solved_celebrated, win_screen_initiated
    if selected_level:
        # Handle both dict and object formats for selected_level
        if isinstance(selected_level, dict):
            # For custom puzzles: don't shuffle initially, apply image, then shuffle
            board = Board(
                rows=selected_level["rows"],
                cols=selected_level["rows"], 
                tile_size=120,
                margin=4,
                is_preview=True  # Don't shuffle in constructor
            )
            # Apply custom image and then shuffle if it's a custom puzzle
            if "custom_image" in selected_level:
                board.apply_custom_image(selected_level["custom_image"])
                board.shuffle(80)  # Manually shuffle after applying image
        else:
            # For regular puzzles: create and shuffle normally
            board = Board(
                rows=selected_level.rows,
                cols=selected_level.rows,
                tile_size=120,
                margin=4,
            )
        hud.move_count = 0
        star_hud.set_rating(0)
        puzzle_solved_celebrated = False  # Reset celebration flag for new game
        win_screen_initiated = False # Reset win screen flag

def start_game(level_info):
    global game_state, board, selected_level, hud, star_hud, puzzle_solved_celebrated, win_screen_initiated
    selected_level = level_info
    board = Board(
        rows=level_info.rows,
        cols=level_info.rows,
        tile_size=120,
        margin=4,
    )
    hud.move_count = 0
    game_state = STATE_PLAYING
    star_hud.set_rating(0)
    puzzle_solved_celebrated = False  # Reset celebration flag for new game
    win_screen_initiated = False # Reset win screen flag

def start_custom_game(level_info):
    global game_state, board, selected_level, hud, star_hud, puzzle_solved_celebrated, win_screen_initiated
    selected_level = level_info
    # Create the board without shuffling initially
    board = Board(
        rows=level_info["rows"],
        cols=level_info["rows"],
        tile_size=120,
        margin=4,
        is_preview=True  # Don't shuffle in constructor
    )
    
    # Apply the custom image to the tiles in their initial positions
    if "custom_image" in level_info:
        board.apply_custom_image(level_info["custom_image"])
    
    # Now shuffle the board to create the puzzle
    board.shuffle(80)
    
    hud.move_count = 0
    game_state = STATE_PLAYING
    star_hud.set_rating(0)
    puzzle_solved_celebrated = False  # Reset celebration flag for new game
    win_screen_initiated = False # Reset win screen flag

def init_custom_puzzle_screen():
    global custom_puzzle_screen
    custom_puzzle_screen = CustomPuzzleScreen(
        pygame.Rect(0, 0, *WINDOW_SIZE),
        back_cb=lambda: switch_state(STATE_MENU),
        start_game_cb=start_custom_game
    )
    
def update_menu_with_custom():
    global menu
    # Reinitialize the menu to add custom puzzle button
    menu = Menu(
        pygame.Rect(0, 0, *WINDOW_SIZE),
        start_cb=lambda: switch_state(STATE_LEVEL_SELECT),
        settings_cb=lambda: switch_state(STATE_SETTINGS),
        quit_cb=quit_game,
    )
    # Add custom puzzle button
    custom_rect = pygame.Rect(0, 0, 250, 60)
    custom_rect.centerx = WINDOW_SIZE[0] // 2
    # Position the custom puzzle button between the settings and quit buttons
    # The original buttons are: Start, Settings, Quit
    # So we need to insert the Custom Puzzle button after Settings
    custom_button = Button(custom_rect, "Custom Puzzle", lambda: switch_state(STATE_CUSTOM_PUZZLE))
    
    # Instead of updating the Menu class, we'll directly modify this menu after creating it
    # We'll reinitialize the menu with all buttons including custom puzzle
    btn_w, btn_h = 250, 60
    spacing = 50
    cx = WINDOW_SIZE[0] // 2
    start_y = (WINDOW_SIZE[1] - 4 * (btn_h + spacing)) // 2 + 80  # Adjusted for 4 buttons
    
    # Create new buttons with custom puzzle added
    start_rect = pygame.Rect(0, 0, btn_w, btn_h)
    start_rect.centerx = cx
    start_rect.y = start_y
    
    settings_rect = pygame.Rect(0, 0, btn_w, btn_h)
    settings_rect.centerx = cx
    settings_rect.y = start_y + btn_h + spacing
    
    custom_rect = pygame.Rect(0, 0, btn_w, btn_h)
    custom_rect.centerx = cx
    custom_rect.y = start_y + 2 * (btn_h + spacing)
    
    quit_rect = pygame.Rect(0, 0, btn_w, btn_h)
    quit_rect.centerx = cx
    quit_rect.y = start_y + 3 * (btn_h + spacing)
    
    menu.buttons = [
        Button(start_rect, "Start", lambda: switch_state(STATE_LEVEL_SELECT)),
        Button(settings_rect, "Settings", lambda: switch_state(STATE_SETTINGS)),
        Button(custom_rect, "Custom Puzzle", lambda: switch_state(STATE_CUSTOM_PUZZLE)),
        Button(quit_rect, "Quit", quit_game),
    ]

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

# Initialize custom puzzle screen after all functions are defined
custom_puzzle_screen = CustomPuzzleScreen(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    back_cb=lambda: switch_state(STATE_MENU),  # Back from Custom Puzzle goes to main menu
    start_game_cb=start_custom_game,
    gallery_cb=lambda: switch_state(STATE_GALLERY)  # Gallery callback
)

# Initialize gallery screen after all functions are defined
gallery_screen = GalleryScreen(
    pygame.Rect(0, 0, *WINDOW_SIZE),
    back_cb=lambda: switch_state(STATE_MENU)
)

# Add gallery instance for saving
gallery = Gallery()

# Initialize win screen after all functions are defined
win_screen = None

# Initialize celebration overlay after all functions are defined
celebration_overlay = CelebrationOverlay()

# Initialize the settings button as a separate UI element (it will be drawn separately)
from ui import Button
settings_btn_size = 60
menu_settings_button = Button(
    pygame.Rect(WINDOW_SIZE[0] - settings_btn_size - 15, 15, settings_btn_size, settings_btn_size),
    "⚙",  # Settings gear icon (using character)
    lambda: switch_state(STATE_SETTINGS),
    bg_color=(85, 120, 100),  # More vibrant green for better visibility
    txt_color=(255, 255, 255),  # White text for contrast
    image_path='assets/images/button.png'  # Use the button image (relative to working directory)
)

# Add custom puzzle button to the menu (removing Settings and Gallery from main menu)
from ui import Button
w, h = WINDOW_SIZE
btn_w, btn_h = 250, 60
spacing = 60  # Increased spacing for better breathing room between buttons
cx = WINDOW_SIZE[0] // 2

# Calculate total height for 3 buttons (Start, Custom Puzzle, Quit) with consistent spacing
total_menu_height = btn_h * 3 + spacing * 2  # 3 buttons + 2 spaces between
start_y = (h - total_menu_height) // 2 + 100  # Adjusted offset for better vertical centering with fewer buttons

# Create new button positions for: Start, Custom Puzzle, Quit
start_rect = pygame.Rect(0, 0, btn_w, btn_h)
start_rect.centerx = cx
start_rect.y = start_y

custom_rect = pygame.Rect(0, 0, btn_w, btn_h)
custom_rect.centerx = cx
custom_rect.y = start_y + btn_h + spacing

quit_rect = pygame.Rect(0, 0, btn_w, btn_h)
quit_rect.centerx = cx
quit_rect.y = start_y + 2 * (btn_h + spacing)

# Reconstruct the menu buttons with reduced buttons - ensuring consistent styling
# Make "Start" and "Quit" stand out more, and "Custom Puzzle" more subdued to indicate submenu
menu.buttons = [
    Button(start_rect, "Start", lambda: switch_state(STATE_LEVEL_SELECT), bg_color=(100, 150, 120)),  # More prominent green
    Button(custom_rect, "Custom Image", lambda: switch_state(STATE_CUSTOM_PUZZLE), bg_color=(80, 120, 100)),  # More subdued green
    Button(quit_rect, "Quit", quit_game, bg_color=(130, 100, 85)),  # Different color for quit button
]



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
            # Handle settings button event separately
            menu_settings_button.handle_event(event)
        elif game_state == STATE_LEVEL_SELECT:
            level_select.handle_event(event)
        elif game_state == STATE_SETTINGS:
            settings_screen.handle_event(event)
        elif game_state == STATE_CUSTOM_PUZZLE:
            custom_puzzle_screen.handle_event(event)
        elif game_state == STATE_CROPPING:
            if cropping_tool:
                cropping_tool.handle_event(event)
        elif game_state == STATE_GALLERY:  # <-- NEW
            gallery_screen.handle_event(event)
        elif game_state == STATE_GUIDE:
            guide.handle_event(event)
        elif game_state == STATE_WIN:
            if win_screen:
                win_screen.handle_event(event)
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
        # Update settings button animations
        menu_settings_button.update(dt)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.update(dt)
    elif game_state == STATE_SETTINGS:
        settings_screen.update(dt)
    elif game_state == STATE_CUSTOM_PUZZLE:
        custom_puzzle_screen.update(dt)
    elif game_state == STATE_CROPPING:
        if cropping_tool:
            cropping_tool.update(dt)
    elif game_state == STATE_GALLERY:  # <-- NEW
        # Gallery screen doesn't have animations, so no update needed
        pass
    elif game_state == STATE_GUIDE:
        pass # No animations for the guide screen itself
    elif game_state == STATE_WIN:
        if win_screen:
            win_screen.update(dt)
    elif game_state == STATE_PLAYING or game_state == STATE_PAUSED:
        # Update HUD even when playing
        pass  # HUD doesn't currently have animations
        # Update celebration overlay if active
        if board and board.is_solved() and celebration_overlay and celebration_overlay.is_active():
            celebration_overlay.update(dt)

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
        # Draw the settings button in the top-right corner
        menu_settings_button.draw(screen)
    elif game_state == STATE_LEVEL_SELECT:
        level_select.draw(screen)
    elif game_state == STATE_SETTINGS:
        settings_screen.draw(screen)
    elif game_state == STATE_CUSTOM_PUZZLE:
        custom_puzzle_screen.draw(screen)
    elif game_state == STATE_CROPPING:
        if cropping_tool:
            cropping_tool.draw(screen)
    elif game_state == STATE_GALLERY:  # <-- NEW
        gallery_screen.draw(screen)
    elif game_state == STATE_GUIDE:
        # Draw the game in the background
        if board:
            board.draw(screen, pygame.font.SysFont(None, 48))
        hud.draw(screen)

        # Create a solved board for the guide's visual aid
        solved_board_for_guide = None
        if selected_level:
            rows = selected_level.rows if hasattr(selected_level, 'rows') else selected_level['rows']
            # Create a board in its solved state (is_preview=True)
            solved_board_instance = Board(rows=rows, cols=rows, tile_size=40, margin=2, is_preview=True)
            
            # If it's a custom puzzle with an image, apply it
            if isinstance(selected_level, dict) and "custom_image" in selected_level:
                solved_board_instance.apply_custom_image(selected_level["custom_image"])

            # Render the solved board to a smaller surface
            board_width = rows * 40 + (rows + 1) * 2
            board_height = rows * 40 + (rows + 1) * 2
            solved_board_for_guide = pygame.Surface((board_width, board_height))
            solved_board_for_guide.fill(BG_COLOR)
            solved_board_instance.draw_preview(solved_board_for_guide, pygame.font.SysFont(None, 24))

        guide.draw(screen, solved_board_for_guide)
    elif game_state == STATE_WIN:
        if win_screen:
            win_screen.draw(screen)
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
        
        # Check if puzzle is solved and celebration hasn't been triggered yet
        if board.is_solved() and game_state != STATE_WIN:
            rows_value = selected_level["rows"] if isinstance(selected_level, dict) else selected_level.rows
            # Only trigger celebration if it hasn't been triggered yet for this solve
            if not puzzle_solved_celebrated and not celebration_overlay.is_active():
                celebration_overlay.trigger(hud.move_count, rows_value)
                puzzle_solved_celebrated = True  # Mark that celebration has been triggered
            # Update and draw celebration overlay
            if puzzle_solved_celebrated:
                celebration_overlay.update(dt)
                celebration_overlay.draw(screen)
        else:
            # Draw star hud if not celebrating
            star_hud.draw(screen)

        # After celebration finishes, handle completion for all puzzles
        if board.is_solved() and puzzle_solved_celebrated and not celebration_overlay.is_active() and game_state != STATE_WIN and not win_screen_initiated:
            win_screen_initiated = True
            rows_value = selected_level["rows"] if isinstance(selected_level, dict) else selected_level.rows
            rating = StarHUD.compute_rating(rows_value, hud.move_count)
            star_hud.set_rating(rating)
            # No longer tracking best scores - just continue

            # Note: Completion sound is played when celebration starts (in celebration.py)
            # This ensures perfect synchronization with visual effects

            is_custom = isinstance(selected_level, dict) and 'custom_image' in selected_level
            if is_custom:
                cropped_image = board.get_cropped_image()
                if cropped_image:
                    win_screen = WinScreen(
                        screen.get_rect(),
                        cropped_image,
                        rows_value,
                        hud.move_count,
                        back_to_menu_cb=back_to_menu,
                        weave_another_cb=lambda: switch_state(STATE_CUSTOM_PUZZLE),
                        play_completion_sound=False  # Sound already played with celebration
                    )
                    switch_state(STATE_WIN)
            else:
                # For non-custom puzzles, just reset the celebration flag
                # The puzzle remains visible with completion state
                # In the original code, there was no special handling after sound for regular puzzles
                # So we'll just ensure the celebration doesn't retrigger
                pass

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
