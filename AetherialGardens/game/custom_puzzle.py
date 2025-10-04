"""game/custom_puzzle.py – Custom puzzle creation with cropping tool."""

import pygame
from typing import Optional, Callable, Dict, Any
from .image_loader import ImageLoader
from .cropping_tool import CroppingTool

class CustomPuzzleScreen:
    """Screen for creating custom puzzles from user images."""
    
    def __init__(self, screen_rect: pygame.Rect, back_cb: Callable[[], None], 
                 start_game_cb: Callable[[Dict[str, Any]], None]):
        self.rect = screen_rect
        self.back_cb = back_cb
        self.start_game_cb = start_game_cb
        
        self.image_loader = ImageLoader()
        self.cropping_tool = None
        self.status = "Select an image to create your puzzle"
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 36)
        
        # UI Elements
        self._create_ui_elements()
        
    def _create_ui_elements(self):
        """Create all UI buttons and elements."""
        cx, cy = self.rect.centerx, self.rect.centery
        btn_w, btn_h = 250, 60
        
        # Main buttons
        self.select_btn = pygame.Rect(cx - btn_w//2, cy - 100, btn_w, btn_h)
        self.back_btn = pygame.Rect(20, self.rect.height - 70, 100, 50)
    
    def _handle_select_image(self):
        """Handle image selection."""
        if self.image_loader.select_image_file():
            if self.image_loader.load_and_process_image():
                # Create cropping tool with the loaded image
                self.cropping_tool = CroppingTool(
                    self.rect,
                    self.image_loader.processed_image,
                    self.back_cb,
                    self.start_game_cb
                )
                return True
        return False
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        if self.cropping_tool:
            # If cropping tool is active, delegate events to it
            self.cropping_tool.handle_event(event)
        else:
            # Handle image selection
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                
                if self.select_btn.collidepoint(mouse_pos):
                    if self._handle_select_image():
                        return
                
                if self.back_btn.collidepoint(mouse_pos):
                    self.back_cb()
                    return
    
    def update(self, dt):
        """Update animations (currently no animations in this screen)."""
        # The cropping tool doesn't have animations, so no update needed
        pass
    
    def draw(self, surface: pygame.Surface):
        """Draw the custom puzzle screen."""
        if self.cropping_tool:
            # If cropping tool is active, draw it
            self.cropping_tool.draw(surface)
        else:
            # Draw the initial screen
            surface.fill((10, 30, 20))
            
            # Title
            title = self.title_font.render("Custom Puzzle", True, (200, 230, 200))
            surface.blit(title, title.get_rect(center=(self.rect.centerx, 80)))
            
            # Status
            status_surf = self.font.render(self.status, True, (180, 200, 180))
            surface.blit(status_surf, status_surf.get_rect(center=(self.rect.centerx, 140)))
            
            # Select button
            pygame.draw.rect(surface, (70, 120, 90), self.select_btn)
            pygame.draw.rect(surface, (30, 60, 45), self.select_btn, 2)
            select_text = self.font.render("Select Image", True, (255, 255, 255))
            select_rect = select_text.get_rect(center=self.select_btn.center)
            surface.blit(select_text, select_rect)
            
            # Back button
            pygame.draw.rect(surface, (120, 100, 75), self.back_btn)
            pygame.draw.rect(surface, (85, 65, 45), self.back_btn, 2)
            back_text = self.font.render("Back", True, (255, 255, 255))
            back_rect = back_text.get_rect(center=self.back_btn.center)
            surface.blit(back_text, back_rect)