"""game/custom_puzzle.py – Custom puzzle creation from user images."""

import pygame
from typing import Optional, Callable
from .image_loader import ImageLoader
from .puzzle import Board
from .ui import Button
from .star import StarHUD

class CustomPuzzleScreen:
    """Screen for creating and playing custom puzzles from user images."""
    
    def __init__(
        self,
        screen_rect: pygame.Rect,
        back_cb: Callable[[], None],
        start_game_cb: Callable[[dict], None]
    ):
        self.rect = screen_rect
        self.back_cb = back_cb
        self.start_game_cb = start_game_cb
        
        # Image loader for handling file selection and processing
        self.image_loader = ImageLoader()
        
        # UI elements
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 48)
        self.message_font = pygame.font.SysFont(None, 24)
        
        # Buttons
        btn_w, btn_h = 250, 60
        btn_x = screen_rect.centerx - btn_w // 2
        
        # Select image button
        self.select_btn = Button(
            pygame.Rect(btn_x, 200, btn_w, btn_h),
            "Select Image",
            self._select_image
        )
        
        # Start puzzle button (initially disabled)
        self.start_btn = Button(
            pygame.Rect(btn_x, 280, btn_w, btn_h),
            "Start Puzzle",
            self._start_puzzle
        )
        self.start_btn.enabled = False  # Disabled until image is loaded
        
        # Back button
        self.back_btn = Button(
            pygame.Rect(20, screen_rect.height - 70, 100, 50),
            "Back",
            self.back_cb
        )
        
        # Size selection buttons
        self.size_buttons = []
        size_btn_w, size_btn_h = 80, 40
        size_btn_y = 360
        sizes = [3, 4, 5]
        size_btn_x_start = screen_rect.centerx - (len(sizes) * size_btn_w + (len(sizes) - 1) * 20) // 2
        
        for i, size in enumerate(sizes):
            btn = Button(
                pygame.Rect(size_btn_x_start + i * (size_btn_w + 20), size_btn_y, size_btn_w, size_btn_h),
                f"{size}x{size}",
                lambda size=size: self._select_size(size)
            )
            self.size_buttons.append((btn, size))
        
        self.selected_size = 3  # Default size
        self.size_buttons[0][0].bg_color = (90, 140, 110)  # Highlight default
        
        # Status message
        self.status_message = "Select an image to create a custom puzzle"
        
        # Preview image
        self.preview_image = None
        self.preview_rect = None
        
    def _select_image(self):
        """Handle image selection button click."""
        if self.image_loader.select_image_file():
            if self.image_loader.load_and_process_image():
                self.status_message = "Image loaded successfully! Select puzzle size and start."
                self.start_btn.enabled = True
                
                # Create preview
                self._create_preview()
            else:
                self.status_message = "Error loading image. Please try another file."
                self.start_btn.enabled = False
        else:
            self.status_message = "No image selected."
            self.start_btn.enabled = False
    
    def _create_preview(self):
        """Create a preview of the loaded image."""
        image = self.image_loader.get_image_surface()
        if not image:
            return
            
        # Calculate preview size (max 300x300)
        max_size = 300
        img_width, img_height = image.get_size()
        
        if img_width > img_height:
            new_width = min(max_size, img_width)
            new_height = int(img_height * (new_width / img_width))
        else:
            new_height = min(max_size, img_height)
            new_width = int(img_width * (new_height / img_height))
            
        self.preview_image = pygame.transform.scale(image, (new_width, new_height))
        
        # Center the preview
        preview_x = self.rect.centerx - new_width // 2
        preview_y = 450
        self.preview_rect = pygame.Rect(preview_x, preview_y, new_width, new_height)
    
    def _select_size(self, size):
        """Handle puzzle size selection."""
        self.selected_size = size
        
        # Update button colors to show selection
        for btn, btn_size in self.size_buttons:
            if btn_size == size:
                btn.bg_color = (90, 140, 110)  # Highlight selected
            else:
                btn.bg_color = (70, 120, 90)  # Default color
    
    def _start_puzzle(self):
        """Start the puzzle with the selected image and size."""
        if not self.image_loader.get_image_surface():
            self.status_message = "No image loaded. Please select an image first."
            return
            
        # Create level info for the custom puzzle
        level_info = {
            "name": f"Custom {self.selected_size}×{self.selected_size}",
            "rows": self.selected_size,
            "bg_path": None,  # We'll use the custom image instead
            "custom_image": self.image_loader.get_image_surface()
        }
        
        # Start the game with the custom puzzle
        self.start_game_cb(level_info)
    
    def handle_event(self, event):
        """Handle pygame events."""
        self.select_btn.handle_event(event)
        self.start_btn.handle_event(event)
        self.back_btn.handle_event(event)
        
        for btn, _ in self.size_buttons:
            btn.handle_event(event)
    
    def update(self, dt):
        """Update animations."""
        self.select_btn.update(dt)
        self.start_btn.update(dt)
        self.back_btn.update(dt)
        
        for btn, _ in self.size_buttons:
            btn.update(dt)
    
    def draw(self, surface):
        """Draw the custom puzzle screen."""
        # Background
        surface.fill((10, 30, 20))
        
        # Title
        title = self.title_font.render("Custom Puzzle", True, (200, 230, 200))
        title_rect = title.get_rect(center=(self.rect.centerx, 80))
        surface.blit(title, title_rect)
        
        # Status message
        msg = self.message_font.render(self.status_message, True, (180, 200, 180))
        msg_rect = msg.get_rect(center=(self.rect.centerx, 140))
        surface.blit(msg, msg_rect)
        
        # Buttons
        self.select_btn.draw(surface)
        self.start_btn.draw(surface)
        self.back_btn.draw(surface)
        
        # Size selection label
        size_label = self.font.render("Puzzle Size:", True, (200, 220, 200))
        size_label_rect = size_label.get_rect(center=(self.rect.centerx, 330))
        surface.blit(size_label, size_label_rect)
        
        # Size buttons
        for btn, _ in self.size_buttons:
            btn.draw(surface)
        
        # Preview image
        if self.preview_image and self.preview_rect:
            # Draw border
            pygame.draw.rect(surface, (70, 120, 90), self.preview_rect, 2)
            # Draw image
            surface.blit(self.preview_image, self.preview_rect)