"""game/celebration.py – Celebration overlay shown when puzzle is solved."""

import pygame
from typing import Tuple, Optional
import sys

# Import audio system for celebration sound
try:
    from .audio import play
except ImportError:
    def play(sound_name):
        # Fallback function if audio module is not available
        pass

class CelebrationOverlay:
    """Celebration overlay that appears when puzzle is solved."""
    
    def __init__(self):
        self.active = False
        self.alpha = 0
        self.max_alpha = 200  # Semi-transparent dimming effect
        self.fade_in_speed = 5  # Alpha increase per frame during fade-in
        self.fade_out_speed = 3  # Alpha decrease per frame during fade-out
        self.state = "hidden"  # "hidden", "fading_in", "showing", "fading_out"
        self.show_duration = 2000  # How long to show the celebration in milliseconds
        self.start_time = 0
        
        # Font setup
        self.title_font = pygame.font.SysFont(None, 96)  # Large font for "Puzzle Solved!"
        self.subtitle_font = pygame.font.SysFont(None, 36)  # Smaller font for moves info
        
        # Animation parameters for special effects
        self.particle_system = []
        self.particle_count = 30
        self.particles_active = False
        
    def trigger(self, moves: int = 0, puzzle_size: int = 3) -> None:
        """Trigger the celebration overlay."""
        self.active = True
        self.alpha = 0
        self.state = "fading_in"
        self.start_time = pygame.time.get_ticks()
        self.moves = moves
        self.puzzle_size = puzzle_size
        
        # Play celebration sound
        try:
            play("complete")
        except:
            # If audio fails, continue without sound
            pass
            
    def update(self, dt: int) -> None:
        """Update the celebration overlay state."""
        if not self.active:
            return
            
        current_time = pygame.time.get_ticks()
        
        if self.state == "fading_in":
            # Fade in the overlay
            self.alpha = min(self.alpha + self.fade_in_speed, self.max_alpha)
            if self.alpha >= self.max_alpha:
                self.state = "showing"
                self.start_time = current_time  # Reset timer for showing state
                
        elif self.state == "showing":
            # Stay visible for show_duration
            if current_time - self.start_time >= self.show_duration:
                self.state = "fading_out"
                
        elif self.state == "fading_out":
            # Fade out the overlay
            self.alpha = max(self.alpha - self.fade_out_speed, 0)
            if self.alpha <= 0:
                self.state = "hidden"
                self.active = False
                self.particles_active = False
    
    def is_active(self) -> bool:
        """Check if celebration is still active."""
        return self.active
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the celebration overlay."""
        if not self.active:
            return
            
        # Create a semi-transparent overlay for the dim effect
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Draw the dimming background
        overlay.fill((0, 0, 0, self.alpha))
        surface.blit(overlay, (0, 0))
        
        # Draw the "Puzzle Solved!" text in the center
        if self.state in ["showing", "fading_in"]:
            # "Puzzle Solved!" text - main celebration message
            title_text = self.title_font.render("Puzzle Solved!", True, (255, 255, 100))  # Bright yellow/gold
            title_rect = title_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 50))
            
            # Add a subtle glow effect around the text
            for offset in [-2, -1, 1, 2]:
                glow_text = self.title_font.render("Puzzle Solved!", True, (200, 200, 50))
                surface.blit(glow_text, (title_rect.x + offset, title_rect.y))
                surface.blit(glow_text, (title_rect.x, title_rect.y + offset))
                surface.blit(glow_text, (title_rect.x + offset, title_rect.y + offset))
            
            # Draw the main text
            surface.blit(title_text, title_rect)
            
            # Moves and puzzle size information
            subtitle_text = self.subtitle_font.render(f"Completed in {self.moves} moves ({self.puzzle_size}x{self.puzzle_size})", True, (200, 230, 200))  # Light green
            subtitle_rect = subtitle_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 30))
            surface.blit(subtitle_text, subtitle_rect)
            
            # Additional celebration indicator
            celebration_text = self.subtitle_font.render("🎉 Congratulations! 🎉", True, (255, 200, 100))  # Orange-yellow
            celebration_rect = celebration_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 + 80))
            surface.blit(celebration_text, celebration_rect)