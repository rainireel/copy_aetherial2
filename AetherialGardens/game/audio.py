"""game/audio.py – audio helper with a sound‑effect dictionary and volume control."""

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
    
    # Try different extensions for each sound file to handle both WAV and MP3
    sound_files = {
        "move": ["move.wav", "move.mp3"],
        "place": ["place.mp3", "place.wav"],
        "complete": ["complete.wav", "complete.mp3"],
        "ui": ["ui_click.mp3", "ui_click.wav"]
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
    
    # UI clicks are a little softer by default
    if "ui" in sounds:
        sounds["ui"].set_volume(0.5)
    return sounds

_sounds: dict[str, pygame.mixer.Sound] = {}

def load_sfx():
    """Public wrapper – call after `init_mixer()`."""
    global _sounds
    _sounds = _load_sfx()
    return _sounds["move"]          # legacy compatibility

def load_music():
    """Load the ambient background music."""
    # Try both .wav and .mp3 extensions for ambient music
    base = os.path.join('assets', 'audio')
    music_path = os.path.join(base, 'ambient.wav')
    try:
        pygame.mixer.music.load(music_path)
    except pygame.error:
        music_path = os.path.join(base, 'ambient.mp3')
        pygame.mixer.music.load(music_path)
    
    pygame.mixer.music.set_volume(0.4)

# -----------------------------------------------------------------
# Public helpers used throughout the game
# -----------------------------------------------------------------
def play(name: str) -> None:
    """Play a sound by key (e.g., play('place')). Silently ignore unknown keys."""
    if _sounds:
        snd = _sounds.get(name)
        if snd:
            snd.play()

def play_move() -> None:
    """Legacy function to play move sound for compatibility."""
    play('move')

def set_volume(level: float) -> None:
    """
    Set the master volume for music *and* all SFX.
    ``level`` is a float between 0.0 and 1.0.
    """
    pygame.mixer.music.set_volume(level)
    for snd in _sounds.values():
        snd.set_volume(level)

def start_ambient_loop():
    pygame.mixer.music.play(-1)   # -1 → infinite loop