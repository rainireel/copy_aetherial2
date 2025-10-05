"""game/cropping_tool.py – Interactive image cropping for custom puzzles."""

import pygame
from typing import Tuple, Optional, Callable
from .puzzle import Board

class CropBox:
    """Draggable and resizable square selection box."""
    
    def __init__(self, center: Tuple[int, int], size: int):
        self.center = center
        self.size = size
        self.dragging = False
        self.resizing = False
        self.drag_offset = (0, 0)
        self.corner_size = 12
        self.min_size = 100
        self.max_size = 600
        
    def get_rect(self) -> pygame.Rect:
        """Get the crop box as a pygame.Rect."""
        half_size = self.size // 2
        return pygame.Rect(
            self.center[0] - half_size,
            self.center[1] - half_size,
            self.size,
            self.size
        )
    
    def get_corner_rects(self) -> Tuple[pygame.Rect, pygame.Rect, pygame.Rect, pygame.Rect]:
        """Get rects for the four corner resize handles."""
        rect = self.get_rect()
        return (
            pygame.Rect(rect.left, rect.top, self.corner_size, self.corner_size),
            pygame.Rect(rect.right - self.corner_size, rect.top, self.corner_size, self.corner_size),
            pygame.Rect(rect.left, rect.bottom - self.corner_size, self.corner_size, self.corner_size),
            pygame.Rect(rect.right - self.corner_size, rect.bottom - self.corner_size, self.corner_size, self.corner_size)
        )
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """Handle mouse events for dragging and resizing."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check if clicking on a corner for resizing
            for corner_rect in self.get_corner_rects():
                if corner_rect.collidepoint(mouse_pos):
                    self.resizing = True
                    return True
            
            # Check if clicking inside the box for dragging
            if self.get_rect().collidepoint(mouse_pos):
                self.dragging = True
                self.drag_offset = (
                    mouse_pos[0] - self.center[0],
                    mouse_pos[1] - self.center[1]
                )
                return True
                
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
            self.resizing = False
            
        elif event.type == pygame.MOUSEMOTION:
            mouse_pos = event.pos
            
            if self.dragging:
                self.center = (
                    mouse_pos[0] - self.drag_offset[0],
                    mouse_pos[1] - self.drag_offset[1]
                )
                return True
                
            elif self.resizing:
                # Calculate new size based on distance from center to mouse
                dx = abs(mouse_pos[0] - self.center[0])
                dy = abs(mouse_pos[1] - self.center[1])
                new_size = max(dx, dy) * 2
                self.size = max(self.min_size, min(new_size, self.max_size))
                return True
                
        return False
    
    def draw(self, surface: pygame.Surface):
        """Draw the crop box and resize handles."""
        rect = self.get_rect()
        
        # Draw semi-transparent overlay outside the crop area
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        
        # Cut out the crop area
        crop_area = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        crop_area.fill((0, 0, 0, 0))
        overlay.blit(crop_area, rect.topleft)
        surface.blit(overlay, (0, 0))
        
        # Draw crop box border
        pygame.draw.rect(surface, (255, 255, 255), rect, 2)
        
        # Draw corner handles
        for corner_rect in self.get_corner_rects():
            pygame.draw.rect(surface, (255, 255, 0), corner_rect)

class CroppingTool:
    """Interactive cropping tool with live puzzle preview."""
    
    def __init__(self, screen_rect: pygame.Rect, image: pygame.Surface, 
                 back_cb: Callable[[], None], start_game_cb: Callable[[dict], None]):
        self.rect = screen_rect
        self.image = image
        self.back_cb = back_cb
        self.start_game_cb = start_game_cb
        
        # Scale image to fit screen if needed
        self._scale_image()
        
        # Initialize crop box (centered, 300x300)
        self.crop_box = CropBox(
            (self.image_rect.centerx, self.image_rect.centery),
            min(300, min(self.image_rect.width, self.image_rect.height))
        )
        
        # Grid size selection
        self.grid_size = 3
        self.size_buttons = []
        self._create_size_buttons()
        
        # Preview board
        self.preview_board = None
        self._update_preview()
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 36)
        
        # Buttons
        self.back_btn = pygame.Rect(20, screen_rect.height - 70, 100, 50)
        self.start_btn = pygame.Rect(
            screen_rect.right - 270, 
            screen_rect.height - 70, 
            250, 50
        )
    
    def _scale_image(self):
        """Scale image to fit screen while maintaining aspect ratio."""
        screen_w, screen_h = self.rect.width, self.rect.height
        img_w, img_h = self.image.get_size()
        
        # Calculate scaling to fit screen with some padding
        scale = min(
            (screen_w - 100) / img_w,
            (screen_h - 200) / img_h,
            1.0  # Don't upscale
        )
        
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        self.scaled_image = pygame.transform.scale(self.image, (new_w, new_h))
        
        # Center the image
        self.image_rect = self.scaled_image.get_rect(
            center=(self.rect.centerx, self.rect.centery - 50)
        )
    
    def _create_size_buttons(self):
        """Create grid size selection buttons."""
        button_y = self.rect.height - 140
        button_spacing = 20
        button_w, button_h = 80, 40
        
        start_x = self.rect.centerx - (3 * button_w + 2 * button_spacing) // 2
        
        for i, size in enumerate([3, 4, 5]):
            x = start_x + i * (button_w + button_spacing)
            self.size_buttons.append((
                pygame.Rect(x, button_y, button_w, button_h),
                size
            ))
    
    def _update_preview(self):
        """Update the puzzle preview based on current crop and grid size."""
        # Get the cropped area
        crop_rect = self.crop_box.get_rect()
        
        # Adjust for image position
        adjusted_rect = pygame.Rect(
            crop_rect.left - self.image_rect.left,
            crop_rect.top - self.image_rect.top,
            crop_rect.width,
            crop_rect.height
        )
        
        # Extract the cropped image
        try:
            cropped = self.scaled_image.subsurface(adjusted_rect).copy()
            
            # Create a small preview board
            tile_size = 40
            margin = 2
            board_size = self.grid_size * tile_size + (self.grid_size + 1) * margin
            
            self.preview_board = Board(
                rows=self.grid_size,
                cols=self.grid_size,
                tile_size=tile_size,
                margin=margin
            )
            
            # Apply the cropped image to the preview board
            self.preview_board.apply_custom_image(cropped)
            
            # Position the preview
            self.preview_rect = pygame.Rect(
                self.rect.right - board_size - 20,
                100,
                board_size,
                board_size
            )
            
        except pygame.error:
            # If crop is outside image bounds, create empty preview
            self.preview_board = None
    
    def handle_event(self, event: pygame.event.Event):
        """Handle pygame events."""
        # Handle crop box interactions
        if self.crop_box.handle_event(event):
            self._update_preview()
            return
        
        # Handle size button clicks
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            for btn_rect, size in self.size_buttons:
                if btn_rect.collidepoint(mouse_pos):
                    self.grid_size = size
                    self._update_preview()
                    return
            
            # Handle back button
            if self.back_btn.collidepoint(mouse_pos):
                self.back_cb()
                return
            
            # Handle start button
            if self.start_btn.collidepoint(mouse_pos):
                self._start_puzzle()
                return
    
    def update(self, dt):
        """Update animations (currently no animations in this screen)."""
        # The cropping tool doesn't have animations, so no update needed
        pass
    
    def _start_puzzle(self):
        """Start the puzzle with the cropped image."""
        # Get the cropped area
        crop_rect = self.crop_box.get_rect()
        
        # Adjust for image position
        adjusted_rect = pygame.Rect(
            crop_rect.left - self.image_rect.left,
            crop_rect.top - self.image_rect.top,
            crop_rect.width,
            crop_rect.height
        )
        
        # Extract the cropped image
        try:
            cropped = self.scaled_image.subsurface(adjusted_rect).copy()
            
            # Create level info
            level_info = {
                "name": f"Custom {self.grid_size}×{self.grid_size}",
                "rows": self.grid_size,
                "custom_image": cropped
            }
            
            self.start_game_cb(level_info)
        except pygame.error:
            print("Error: Crop area outside image bounds")
    
    def draw(self, surface: pygame.Surface):
        """Draw the cropping interface."""
        surface.fill((10, 30, 20))
        
        # Draw title
        title = self.title_font.render("Crop Your Puzzle", True, (200, 230, 200))
        surface.blit(title, title.get_rect(center=(self.rect.centerx, 40)))
        
        # Draw the image
        surface.blit(self.scaled_image, self.image_rect)
        
        # Draw the crop box
        self.crop_box.draw(surface)
        
        # Draw preview label
        preview_label = self.font.render("Preview", True, (200, 220, 200))
        surface.blit(preview_label, (self.rect.right - 150, 70))
        
        # Draw preview board
        if self.preview_board and self.preview_rect:
            # Draw preview background
            pygame.draw.rect(surface, (30, 60, 45), self.preview_rect)
            pygame.draw.rect(surface, (70, 120, 90), self.preview_rect, 2)
            
            # Create a temporary surface for the preview
            preview_surface = pygame.Surface(self.preview_rect.size)
            self.preview_board.draw(preview_surface, pygame.font.SysFont(None, 24))
            surface.blit(preview_surface, self.preview_rect)
        
        # Draw size buttons
        for btn_rect, size in self.size_buttons:
            color = (90, 140, 110) if size == self.grid_size else (70, 120, 90)
            pygame.draw.rect(surface, color, btn_rect)
            pygame.draw.rect(surface, (30, 60, 45), btn_rect, 2)
            
            size_text = self.font.render(f"{size}x{size}", True, (255, 255, 255))
            text_rect = size_text.get_rect(center=btn_rect.center)
            surface.blit(size_text, text_rect)
        
        # Draw back button
        pygame.draw.rect(surface, (120, 100, 75), self.back_btn)
        pygame.draw.rect(surface, (85, 65, 45), self.back_btn, 2)
        back_text = self.font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_btn.center)
        surface.blit(back_text, back_rect)
        
        # Draw start button
        pygame.draw.rect(surface, (70, 120, 90), self.start_btn)
        pygame.draw.rect(surface, (30, 60, 45), self.start_btn, 2)
        start_text = self.font.render("Start Puzzle", True, (255, 255, 255))
        start_rect = start_text.get_rect(center=self.start_btn.center)
        surface.blit(start_text, start_rect)