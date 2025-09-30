"""game/main.py – entry point for Aetherial Gardens (MVP skeleton).
Runs a simple 800×600 Pygame window with a dark‑green background.
"""

import sys
import pygame

# Handle both direct execution and module import
try:
    from .puzzle import Board
    from .ui import Menu, HUD
    from .audio import init_mixer, load_sfx, load_music, play_move, start_ambient_loop
    from .save import load_progress, save_progress
except ImportError:
    from puzzle import Board
    from ui import Menu, HUD
    from audio import init_mixer, load_sfx, load_music, play_move, start_ambient_loop
    from save import load_progress, save_progress

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
# Initialise audio first (must be after pygame.init())
# -----------------------------------------------------------------
init_mixer()
_move_sfx = load_sfx() # store in module‑level variable
load_music()
start_ambient_loop()

# -----------------------------------------------------------------
# Game state flags
# -----------------------------------------------------------------
STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"

# Load saved progress
save_data = load_progress()
best_moves = save_data.get("best_moves", None)
garden_unlocked = save_data.get("unlocked", True)

# Main loop – keep the window responsive until the user closes it.
running = True
game_state = STATE_MENU

# Define functions after global variables are set up
def toggle_pause():
    global game_state
    if game_state == STATE_PLAYING:
        game_state = STATE_PAUSED
    elif game_state == STATE_PAUSED:
        game_state = STATE_PLAYING

def start_game():
    global game_state, board, hud
    
    def handle_move_local():
        hud.increment_moves()
        play_move()
    
    board = Board(rows=3, cols=3, tile_size=150, margin=5, on_move_callback=handle_move_local) # fresh scramble
    hud.move_count = 0
    game_state = STATE_PLAYING

def quit_game():
    global running
    # Save the current best moves before quitting
    save_data = {
        "best_moves": best_moves,
        "unlocked": garden_unlocked
    }
    save_progress(save_data)
    running = False

# -----------------------------------------------------------------
# Initialise objects that live across states
# -----------------------------------------------------------------
def handle_move():
    hud.increment_moves()
    play_move()

hud = HUD(pygame.Rect(0, 0, *WINDOW_SIZE), pause_cb=toggle_pause)
menu = Menu(pygame.Rect(0, 0, *WINDOW_SIZE), start_cb=start_game, quit_cb=quit_game)

# Initialize the board after HUD is created, so we can pass the move callback
board = Board(rows=3, cols=3, tile_size=150, margin=5, on_move_callback=handle_move)
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == STATE_MENU:
            menu.handle_event(event)
        elif game_state == STATE_PLAYING:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                board.click_at(event.pos)  # This handles move counter and SFX internally
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
        # If paused, add a semi-transparent overlay
        if game_state == STATE_PAUSED:
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))  # Semi-transparent dark layer
            screen.blit(overlay, (0, 0))
            # Show "PAUSED" text
            paused_text = pygame.font.SysFont(None, 64).render("PAUSED", True, (255, 255, 255))
            text_rect = paused_text.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2))
            screen.blit(paused_text, text_rect)
        if board.is_solved():
            # Check for best move count
            if best_moves is None or hud.move_count < best_moves:
                best_moves = hud.move_count
                # Save the new best score
                save_data = {
                    "best_moves": best_moves,
                    "unlocked": garden_unlocked
                }
                save_progress(save_data)
            
            overlay = pygame.Surface(WINDOW_SIZE, pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 120))
            screen.blit(overlay, (0, 0))
            # Show both "Puzzle solved!" and best moves
            msg = pygame.font.SysFont(None, 72).render("Puzzle solved!", True, (255, 255, 255))
            msg_rect = msg.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 - 30))
            screen.blit(msg, msg_rect)
            
            # Show best move count
            if best_moves is not None:
                best_msg = pygame.font.SysFont(None, 36).render(f"Best: {best_moves} moves", True, (255, 255, 100))
                best_rect = best_msg.get_rect(center=(WINDOW_SIZE[0] // 2, WINDOW_SIZE[1] // 2 + 30))
                screen.blit(best_msg, best_rect)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()