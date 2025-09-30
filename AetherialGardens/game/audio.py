"""game/audio.py – minimal audio helper for the MVP.
Only pygame.mixer is used; all paths are relative to the project root.
"""

import os
import pygame

# ---------------------------------------------------------------------
# Global variables to store loaded sounds
# ---------------------------------------------------------------------
_move_sfx = None

# ---------------------------------------------------------------------
# Initialise the mixer – must happen after pygame.init() but before any sound load.
# ---------------------------------------------------------------------
def init_mixer():
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ---------------------------------------------------------------------
# Load assets (call once at start‑up).
# ---------------------------------------------------------------------
def load_sfx():
    global _move_sfx
    # Try different possible file names for move sound
    move_paths = [
        os.path.join('assets', 'audio', 'move.wav'),
        os.path.join('assets', 'audio', 'move.mp3')
    ]
    
    for path in move_paths:
        try:
            _move_sfx = pygame.mixer.Sound(path)
            return _move_sfx
        except (pygame.error, FileNotFoundError):
            continue
    
    # If no file found, return None
    _move_sfx = None
    return _move_sfx

def load_music():
    # Try different possible file names for music
    music_paths = [
        os.path.join('assets', 'audio', 'ambient.mp3'),
        os.path.join('assets', 'audio', 'ambient.wav')
    ]
    
    for path in music_paths:
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(0.4) # soft background level
            return
        except (pygame.error, FileNotFoundError):
            continue

# ---------------------------------------------------------------------
# Public helper functions used by the game loop.
# ---------------------------------------------------------------------
def play_move():
    global _move_sfx
    if _move_sfx:
        _move_sfx.play()

def start_ambient_loop():
    pygame.mixer.music.play(-1)  # -1 → infinite loop