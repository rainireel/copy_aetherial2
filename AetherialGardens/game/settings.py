"""game/settings.py – volume slider and mute toggle."""

import pygame
from typing import Callable, Tuple


class SettingsScreen:
    """
    Settings screen with volume slider and mute toggle.
    """
    
    def __init__(self, screen_rect: pygame.Rect, back_cb: Callable[[], None], 
                 volume_change_cb: Callable[[float], None] = None, 
                 mute_change_cb: Callable[[bool], None] = None):
        self.back_cb = back_cb
        self.volume_change_cb = volume_change_cb  # Callback when volume changes
        self.mute_change_cb = mute_change_cb     # Callback when mute changes
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        
        # Volume slider properties
        self.slider_rect = pygame.Rect(0, 0, 300, 20)
        self.slider_rect.center = (screen_rect.centerx, screen_rect.centery - 30)
        
        # Mute toggle properties
        self.mute_rect = pygame.Rect(0, 0, 20, 20)
        self.mute_rect.center = (screen_rect.centerx + 160, screen_rect.centery + 30)
        
        # Back button
        back_btn_width, back_btn_height = 120, 40
        self.back_rect = pygame.Rect(
            screen_rect.centerx - back_btn_width // 2,
            screen_rect.centery + 100,
            back_btn_width,
            back_btn_height
        )
        
        # Current settings (will be set externally)
        self.volume = 0.4
        self.muted = False

    def set_volume(self, vol: float) -> None:
        """Update the displayed volume."""
        self.volume = max(0.0, min(1.0, vol))  # Clamp between 0 and 1

    def set_muted(self, muted: bool) -> None:
        """Update the mute state."""
        self.muted = muted
    
    def get_volume(self) -> float:
        """Get the current volume setting."""
        return self.volume
        
    def is_muted(self) -> bool:
        """Get the current mute setting."""
        return self.muted

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle input events."""
        old_volume = self.volume
        old_muted = self.muted
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Check if volume slider clicked
            if self.slider_rect.collidepoint(event.pos):
                # Calculate volume based on mouse position
                rel_x = event.pos[0] - self.slider_rect.left
                self.volume = max(0.0, min(1.0, rel_x / self.slider_rect.width))
            
            # Check if mute toggle clicked
            elif self.mute_rect.collidepoint(event.pos):
                self.muted = not self.muted
                
            # Check if back button clicked
            elif self.back_rect.collidepoint(event.pos):
                self.back_cb()

        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:  # Dragging
            # Adjust volume while dragging on slider
            if self.slider_rect.collidepoint(event.pos):
                rel_x = event.pos[0] - self.slider_rect.left
                self.volume = max(0.0, min(1.0, rel_x / self.slider_rect.width))
        
        # Call callbacks if values changed
        if old_volume != self.volume and self.volume_change_cb:
            self.volume_change_cb(self.volume)
        if old_muted != self.muted and self.mute_change_cb:
            self.mute_change_cb(self.muted)

    def draw(self, surf: pygame.Surface) -> None:
        """Draw the settings screen."""
        # Dark overlay background
        overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surf.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("Settings", True, (200, 230, 200))
        title_rect = title.get_rect(center=(surf.get_width() // 2, 100))
        surf.blit(title, title_rect)

        # Volume label
        vol_label = self.font.render("Volume", True, (220, 220, 220))
        surf.blit(vol_label, (self.slider_rect.left - 100, self.slider_rect.top - 5))

        # Volume slider track
        pygame.draw.rect(surf, (60, 80, 70), self.slider_rect)
        pygame.draw.rect(surf, (30, 50, 40), self.slider_rect, 2)

        # Volume slider thumb
        thumb_x = self.slider_rect.left + int(self.volume * self.slider_rect.width)
        thumb_rect = pygame.Rect(thumb_x - 5, self.slider_rect.top - 5, 10, self.slider_rect.height + 10)
        pygame.draw.rect(surf, (100, 150, 120), thumb_rect)
        pygame.draw.rect(surf, (70, 100, 90), thumb_rect, 2)

        # Mute toggle
        mute_label = self.font.render("Mute", True, (220, 220, 220))
        surf.blit(mute_label, (self.mute_rect.left - 70, self.mute_rect.top - 5))
        
        # Draw mute checkbox
        pygame.draw.rect(surf, (60, 80, 70), self.mute_rect)
        pygame.draw.rect(surf, (30, 50, 40), self.mute_rect, 2)
        if self.muted:
            # Draw X in checkbox
            pygame.draw.line(surf, (220, 100, 100), self.mute_rect.topleft, self.mute_rect.bottomright, 2)
            pygame.draw.line(surf, (220, 100, 100), self.mute_rect.topright, self.mute_rect.bottomleft, 2)

        # Draw current volume percentage
        vol_text = self.font.render(f"{int(self.volume * 100)}%", True, (200, 220, 200))
        surf.blit(vol_text, (self.slider_rect.right + 15, self.slider_rect.top - 5))

        # Back button
        pygame.draw.rect(surf, (70, 100, 85), self.back_rect, border_radius=8)
        pygame.draw.rect(surf, (40, 70, 55), self.back_rect, 2, border_radius=8)
        back_text = self.font.render("Back", True, (240, 240, 240))
        back_text_rect = back_text.get_rect(center=self.back_rect.center)
        surf.blit(back_text, back_text_rect)