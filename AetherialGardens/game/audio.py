"""game/audio.py – audio helper with a sound‑effect dictionary.

The module now loads:
* move.*            – generic tile‑slide SFX (tries .mp3 first, then .wav)
* place.*           – sound for a *correct* tile placement (tries .mp3 first, then .wav)  
* complete.*        – chime when the puzzle is solved (tries .mp3 first, then .wav)
* ui_click.*        – UI button click feedback (tries .mp3 first, then .wav)
"""

import os
import pygame

# -----------------------------------------------------------------
# Initialise the mixer – must happen after pygame.init()
# -----------------------------------------------------------------
def init_mixer():
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# -----------------------------------------------------------------
# Load all SFX into a dictionary for easy lookup
# -----------------------------------------------------------------
def _load_sfx() -> dict[str, pygame.mixer.Sound]:
    base = os.path.join('assets', 'audio')
    sounds = {}
    
    # List of sounds to try loading (prioritizing existing files)
    sound_files = {
        "move": ["move.wav", "move.mp3"],           # move.wav is the new file you added
        "place": ["place.mp3", "place.wav"],       # place.mp3 exists, will try place.wav as fallback
        "complete": ["complete.wav", "complete.mp3"], # complete.wav is the new file you added
        "ui": ["ui_click.mp3", "ui_click.wav"]     # ui_click.mp3 exists, will try ui_click.wav as fallback
    }
    
    for key, filenames in sound_files.items():
        sound = None
        for filename in filenames:
            try:
                sound_path = os.path.join(base, filename)
                sound = pygame.mixer.Sound(sound_path)
                break  # If successful, break out of the filename loop
            except pygame.error:
                continue  # Try next extension
        
        if sound:
            sounds[key] = sound
        else:
            print(f"Warning: Could not load sound file for '{key}'")
    
    # Lower volume a little for UI clicks so they don't dominate
    if "ui" in sounds:
        sounds["ui"].set_volume(0.5)
    return sounds

# The dictionary is created once at import time (after init_mixer() is called)
_sounds: dict[str, pygame.mixer.Sound] = {}

def load_sfx():
    """Public wrapper – call after `init_mixer()`."""
    global _sounds
    _sounds = _load_sfx()
    # Return the move sound for legacy compatibility, or None if not found
    return _sounds.get("move")

def load_music():
    """Load the ambient background music."""
    music_path = os.path.join('assets', 'audio', 'ambient.wav')
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.4)  # soft background level

# -----------------------------------------------------------------
# Public helpers used throughout the game
# -----------------------------------------------------------------
def play(name: str) -> None:
    """Play a sound by key (e.g., ``play('place')``). Silently ignore unknown keys."""
    if _sounds:
        snd = _sounds.get(name)
        if snd:
            snd.play()

def play_move() -> None:
    """Legacy function to play move sound for compatibility."""
    play('move')

def set_volume(vol: float) -> None:
    """Set volume for all SFX and music (0.0 to 1.0)."""
    global _sounds
    for sound in _sounds.values():
        sound.set_volume(vol)
    pygame.mixer.music.set_volume(vol)

def start_ambient_loop():
    pygame.mixer.music.play(-1)   # -1 → infinite loop