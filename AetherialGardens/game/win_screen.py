"""game/win_screen.py – Screen shown when puzzle is solved."""

import pygame
from typing import Callable, Optional
import os
from .gallery import Gallery

class WinScreen:
    """Screen shown when the puzzle is solved."""
    
    def __init__(self, 
                 screen_rect: pygame.Rect, 
                 cropped_image: pygame.Surface,
                 puzzle_size: int,
                 moves: int,
                 back_to_menu_cb: Callable[[], None],
                 weave_another_cb: Callable[[], None]):
        self.rect = screen_rect
        self.cropped_image = cropped_image
        self.puzzle_size = puzzle_size
        self.moves = moves
        self.back_to_menu_cb = back_to_menu_cb
        self.weave_another_cb = weave_another_cb
        
        # Gallery for saving
        self.gallery = Gallery()
        self.save_confirmation = False
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 72)
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 28)
        
        # Calculate image dimensions to fit in screen
        img_w, img_h = cropped_image.get_size()
        max_width = screen_rect.width - 100
        max_height = screen_rect.height - 300  # Leave space for buttons and text
        
        scale = min(max_width / img_w, max_height / img_h)
        self.display_w = int(img_w * scale)
        self.display_h = int(img_h * scale)
        
        # Position image in center
        self.display_x = (screen_rect.width - self.display_w) // 2
        self.display_y = 100  # Leave space at top for title
        
        # Buttons
        btn_w, btn_h = 200, 50
        btn_spacing = 20
        start_y = self.display_y + self.display_h + 30
        
        # Center the buttons
        total_btn_width = 3 * btn_w + 2 * btn_spacing
        start_x = (screen_rect.width - total_btn_width) // 2
        
        self.save_btn = pygame.Rect(start_x, start_y, btn_w, btn_h)
        self.another_btn = pygame.Rect(start_x + btn_w + btn_spacing, start_y, btn_w, btn_h)
        self.menu_btn = pygame.Rect(start_x + 2 * (btn_w + btn_spacing), start_y, btn_w, btn_h)
        
        # Calculate star rating
        self.rating = self._calculate_rating()
        
        # Play the completion sound
        try:
            from .audio import play
            play("complete")
        except ImportError:
            pass  # Audio module might not be available in all contexts
    
    def _calculate_rating(self) -> int:
        """Calculate star rating based on puzzle size and moves."""
        # Define target moves for different puzzle sizes for full stars
        target_moves = {
            3: 20,
            4: 80,
            5: 150
        }
        
        # Get target for the puzzle size, defaulting to higher for larger puzzles
        base_target = target_moves.get(self.puzzle_size, self.puzzle_size * self.puzzle_size * 8)
        
        # Calculate rating based on ratio
        if self.moves <= base_target:
            return 3  # 3 stars for good performance
        elif self.moves <= base_target * 1.5:
            return 2  # 2 stars for average performance
        else:
            return 1  # 1 star for slower
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Handle Save to Gallery button
            if self.save_btn.collidepoint(mouse_pos) and not self.save_confirmation:
                # Save to gallery using pygame.image.save() 
                try:
                    self.gallery.save_memory(
                        self.cropped_image,
                        self.puzzle_size,
                        self.moves,
                        self.rating
                    )
                    # Refresh gallery to ensure data consistency
                    self.gallery.refresh_gallery()
                    self.save_confirmation = True
                except Exception as e:
                    print(f"Error saving memory to gallery: {e}")
                    # Optionally show an error message to the user
            
            # Handle "Weave Another" button
            elif self.another_btn.collidepoint(mouse_pos):
                self.weave_another_cb()
            
            # Handle "Back to Loom Menu" button
            elif self.menu_btn.collidepoint(mouse_pos):
                self.back_to_menu_cb()
    
    def update(self, dt: int) -> None:
        """Update animations (currently no animations in this screen)."""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the win screen."""
        surface.fill((10, 30, 20))  # Dark green background
        
        # Draw success message
        message = self.title_font.render("Memory Restored!", True, (255, 255, 200))  # Light yellow
        msg_rect = message.get_rect(center=(self.rect.centerx, 40))
        surface.blit(message, msg_rect)
        
        # Draw the restored image
        scaled_image = pygame.transform.scale(self.cropped_image, (self.display_w, self.display_h))
        surface.blit(scaled_image, (self.display_x, self.display_y))
        
        # Draw info text below the image
        info_text = f"{self.puzzle_size}x{self.puzzle_size} Puzzle • {self.moves} Moves • {self.rating}★"
        info_surface = self.small_font.render(info_text, True, (200, 230, 200))
        info_rect = info_surface.get_rect(center=(self.rect.centerx, self.display_y + self.display_h + 10))
        surface.blit(info_surface, info_rect)
        
        # Draw Save to Gallery button
        btn_color = (70, 120, 90) if not self.save_confirmation else (50, 80, 100)  # Different color when saved
        pygame.draw.rect(surface, btn_color, self.save_btn)
        pygame.draw.rect(surface, (30, 60, 45), self.save_btn, 2)
        
        if not self.save_confirmation:
            save_text = self.font.render("Save to Gallery", True, (255, 255, 255))
        else:
            save_text = self.font.render("Saved!", True, (150, 255, 150))
        
        save_text_rect = save_text.get_rect(center=self.save_btn.center)
        surface.blit(save_text, save_text_rect)
        
        # Draw "Weave Another" button
        pygame.draw.rect(surface, (90, 130, 100), self.another_btn)
        pygame.draw.rect(surface, (50, 90, 70), self.another_btn, 2)
        another_text = self.font.render("Weave Another", True, (255, 255, 255))
        another_text_rect = another_text.get_rect(center=self.another_btn.center)
        surface.blit(another_text, another_text_rect)
        
        # Draw "Back to Loom Menu" button
        pygame.draw.rect(surface, (120, 100, 75), self.menu_btn)
        pygame.draw.rect(surface, (85, 65, 45), self.menu_btn, 2)
        menu_text = self.font.render("Back to Loom Menu", True, (255, 255, 255))
        menu_text_rect = menu_text.get_rect(center=self.menu_btn.center)
        surface.blit(menu_text, menu_text_rect)
        
        # Draw save confirmation message if applicable
        if self.save_confirmation:
            confirm_msg = self.font.render("Memory preserved in your gallery!", True, (150, 255, 150))
            confirm_rect = confirm_msg.get_rect(center=(self.rect.centerx, self.display_y + self.display_h + 120))
            surface.blit(confirm_msg, confirm_rect)