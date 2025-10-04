"""game/gallery.py – Gallery system for saved completed puzzles."""

import os
import json
import uuid
from typing import List, Dict, Optional, Tuple, Callable  # Add Callable import
import pygame
from datetime import datetime

class Gallery:
    """Manages saving and loading of completed puzzle images."""
    
    def __init__(self):
        # Create gallery directory if it doesn't exist
        self.gallery_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "user_memories")
        os.makedirs(self.gallery_dir, exist_ok=True)
        
        # Path to gallery metadata file
        self.gallery_json_path = os.path.join(self.gallery_dir, "gallery.json")
        
        # Ensure gallery.json exists
        self._ensure_gallery_file()
        
        # Load gallery data
        self.gallery_data = self._load_gallery_data()
    
    def _ensure_gallery_file(self) -> None:
        """Create the gallery.json file with defaults if it does not exist."""
        if not os.path.isfile(self.gallery_json_path):
            with open(self.gallery_json_path, "w", encoding="utf-8") as f:
                json.dump({"memories": []}, f, indent=2)
    
    def _load_gallery_data(self) -> Dict:
        """Load gallery data from JSON file."""
        try:
            with open(self.gallery_json_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # If file is corrupted or missing, create a new one
            self._ensure_gallery_file()
            return {"memories": []}
    
    def _save_gallery_data(self) -> None:
        """Save gallery data to JSON file."""
        with open(self.gallery_json_path, "w", encoding="utf-8") as f:
            json.dump(self.gallery_data, f, indent=2)
    
    def save_memory(self, image: pygame.Surface, puzzle_size: int, moves: int, stars: int) -> str:
        """
        Save a completed puzzle image to the gallery.
        
        Args:
            image: The cropped puzzle image
            puzzle_size: The size of the puzzle (e.g., 3 for 3x3)
            moves: Number of moves taken to complete
            stars: Star rating (1-3)
            
        Returns:
            The filename of the saved image
        """
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"memory_{timestamp}_{unique_id}.png"
        filepath = os.path.join(self.gallery_dir, filename)
        
        # Save the image
        pygame.image.save(image, filepath)
        
        # Add to gallery data
        memory_entry = {
            "filename": filename,
            "puzzle_size": puzzle_size,
            "moves": moves,
            "stars": stars,
            "date": datetime.now().isoformat()
        }
        
        self.gallery_data["memories"].append(memory_entry)
        self._save_gallery_data()
        
        return filename
    
    def get_memories(self) -> List[Dict]:
        """Get all saved memories."""
        return self.gallery_data.get("memories", [])
    
    def get_memory_image(self, filename: str) -> Optional[pygame.Surface]:
        """Load a memory image by filename."""
        filepath = os.path.join(self.gallery_dir, filename)
        if os.path.isfile(filepath):
            return pygame.image.load(filepath).convert_alpha()
        return None
    
    def delete_memory(self, filename: str) -> bool:
        """
        Delete a memory image and its metadata.
        
        Args:
            filename: The filename of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        # Delete the image file
        filepath = os.path.join(self.gallery_dir, filename)
        try:
            if os.path.isfile(filepath):
                os.remove(filepath)
        except OSError:
            return False
        
        # Remove from gallery data
        self.gallery_data["memories"] = [
            m for m in self.gallery_data["memories"] 
            if m["filename"] != filename
        ]
        self._save_gallery_data()
        
        return True

class GalleryScreen:
    """UI screen for viewing the gallery of saved memories."""
    
    def __init__(self, screen_rect: pygame.Rect, back_cb: Callable[[], None]):
        self.rect = screen_rect
        self.back_cb = back_cb
        
        # Gallery manager
        self.gallery = Gallery()
        
        # UI state
        self.selected_memory = None
        self.viewing_fullscreen = False
        
        # Thumbnail settings
        self.thumbnail_size = 150
        self.thumbnail_margin = 20
        self.thumbnails_per_row = (screen_rect.width - 40) // (self.thumbnail_size + self.thumbnail_margin)
        
        # Fonts
        self.title_font = pygame.font.SysFont(None, 48)
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # UI elements
        self.back_btn = pygame.Rect(20, screen_rect.height - 70, 100, 50)
        self.fullscreen_back_btn = pygame.Rect(20, 20, 100, 50)
        self.delete_btn = pygame.Rect(screen_rect.width - 120, screen_rect.height - 70, 100, 50)
        
        # Scroll position
        self.scroll_y = 0
        self.max_scroll = 0
        
        # Load thumbnails
        self.thumbnails = []
        self._load_thumbnails()
    
    def _load_thumbnails(self) -> None:
        """Load all memory thumbnails."""
        self.thumbnails = []
        memories = self.gallery.get_memories()
        
        for memory in memories:
            image = self.gallery.get_memory_image(memory["filename"])
            if image:
                # Scale image to thumbnail size
                thumbnail = pygame.transform.scale(image, (self.thumbnail_size, self.thumbnail_size))
                self.thumbnails.append((thumbnail, memory))
        
        # Calculate max scroll
        rows = (len(self.thumbnails) + self.thumbnails_per_row - 1) // self.thumbnails_per_row
        total_height = rows * (self.thumbnail_size + self.thumbnail_margin) + 100  # 100 for title and padding
        self.max_scroll = max(0, total_height - self.rect.height)
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle pygame events."""
        if self.viewing_fullscreen:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.fullscreen_back_btn.collidepoint(event.pos):
                    self.viewing_fullscreen = False
                elif self.delete_btn.collidepoint(event.pos) and self.selected_memory:
                    # Delete the selected memory
                    if self.gallery.delete_memory(self.selected_memory["filename"]):
                        self.selected_memory = None
                        self.viewing_fullscreen = False
                        self._load_thumbnails()
            return
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = event.pos
            
            # Check back button
            if self.back_btn.collidepoint(mouse_pos):
                self.back_cb()
                return
            
            # Check thumbnail clicks
            for i, (thumbnail, memory) in enumerate(self.thumbnails):
                row = i // self.thumbnails_per_row
                col = i % self.thumbnails_per_row
                
                x = 20 + col * (self.thumbnail_size + self.thumbnail_margin)
                y = 100 + row * (self.thumbnail_size + self.thumbnail_margin) - self.scroll_y
                
                thumbnail_rect = pygame.Rect(x, y, self.thumbnail_size, self.thumbnail_size)
                
                if thumbnail_rect.collidepoint(mouse_pos):
                    self.selected_memory = memory
                    self.viewing_fullscreen = True
                    return
        
        elif event.type == pygame.MOUSEWHEEL:
            # Handle scrolling
            self.scroll_y = max(0, min(self.scroll_y - event.y * 20, self.max_scroll))
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the gallery screen."""
        surface.fill((10, 30, 20))
        
        if self.viewing_fullscreen and self.selected_memory:
            self._draw_fullscreen_view(surface)
        else:
            self._draw_thumbnail_view(surface)
    
    def _draw_thumbnail_view(self, surface: pygame.Surface) -> None:
        """Draw the thumbnail grid view."""
        # Title
        title = self.title_font.render("Memory Gallery", True, (200, 230, 200))
        surface.blit(title, title.get_rect(center=(self.rect.centerx, 40)))
        
        # Draw thumbnails
        for i, (thumbnail, memory) in enumerate(self.thumbnails):
            row = i // self.thumbnails_per_row
            col = i % self.thumbnails_per_row
            
            x = 20 + col * (self.thumbnail_size + self.thumbnail_margin)
            y = 100 + row * (self.thumbnail_size + self.thumbnail_margin) - self.scroll_y
            
            # Skip if outside visible area
            if y + self.thumbnail_size < 0 or y > self.rect.height:
                continue
            
            # Draw thumbnail
            surface.blit(thumbnail, (x, y))
            
            # Draw border
            pygame.draw.rect(surface, (70, 120, 90), (x, y, self.thumbnail_size, self.thumbnail_size), 2)
            
            # Draw info
            date_str = memory["date"][:10]  # Just the date part
            info_text = f"{memory['puzzle_size']}x{memory['puzzle_size']} • {memory['moves']} moves • {memory['stars']}★"
            info_surf = self.small_font.render(info_text, True, (180, 200, 180))
            surface.blit(info_surf, (x, y + self.thumbnail_size + 5))
        
        # Draw back button
        pygame.draw.rect(surface, (120, 100, 75), self.back_btn)
        pygame.draw.rect(surface, (85, 65, 45), self.back_btn, 2)
        back_text = self.font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.back_btn.center)
        surface.blit(back_text, back_rect)
        
        # Draw scroll indicator if needed
        if self.max_scroll > 0:
            scroll_height = max(20, self.rect.height * (self.rect.height / (self.rect.height + self.max_scroll)))
            scroll_y = self.rect.height * (self.scroll_y / (self.rect.height + self.max_scroll))
            scroll_rect = pygame.Rect(self.rect.width - 15, scroll_y, 10, scroll_height)
            pygame.draw.rect(surface, (70, 120, 90), scroll_rect)
    
    def _draw_fullscreen_view(self, surface: pygame.Surface) -> None:
        """Draw the fullscreen image view."""
        if not self.selected_memory:
            return
        
        # Load the full image
        image = self.gallery.get_memory_image(self.selected_memory["filename"])
        if not image:
            return
        
        # Scale image to fit screen
        screen_w, screen_h = self.rect.width, self.rect.height
        img_w, img_h = image.get_size()
        
        scale = min(screen_w / img_w, screen_h / img_h)
        new_w, new_h = int(img_w * scale), int(img_h * scale)
        scaled_image = pygame.transform.scale(image, (new_w, new_h))
        
        # Center the image
        img_rect = scaled_image.get_rect(center=(screen_w // 2, screen_h // 2))
        surface.blit(scaled_image, img_rect)
        
        # Draw info panel
        panel_height = 80
        panel_rect = pygame.Rect(0, screen_h - panel_height, screen_w, panel_height)
        panel_surface = pygame.Surface((screen_w, panel_height), pygame.SRCALPHA)
        panel_surface.fill((0, 0, 0, 180))
        surface.blit(panel_surface, (0, screen_h - panel_height))
        
        # Draw info text
        date_str = self.selected_memory["date"][:10]  # Just the date part
        info_text = f"Completed on {date_str} • {self.selected_memory['puzzle_size']}x{self.selected_memory['puzzle_size']} puzzle • {self.selected_memory['moves']} moves • {self.selected_memory['stars']} stars"
        info_surf = self.font.render(info_text, True, (255, 255, 255))
        info_rect = info_surf.get_rect(center=(screen_w // 2, screen_h - panel_height // 2))
        surface.blit(info_surf, info_rect)
        
        # Draw back button
        pygame.draw.rect(surface, (120, 100, 75), self.fullscreen_back_btn)
        pygame.draw.rect(surface, (85, 65, 45), self.fullscreen_back_btn, 2)
        back_text = self.font.render("Back", True, (255, 255, 255))
        back_rect = back_text.get_rect(center=self.fullscreen_back_btn.center)
        surface.blit(back_text, back_rect)
        
        # Draw delete button
        pygame.draw.rect(surface, (150, 50, 50), self.delete_btn)
        pygame.draw.rect(surface, (100, 30, 30), self.delete_btn, 2)
        delete_text = self.font.render("Delete", True, (255, 255, 255))
        delete_rect = delete_text.get_rect(center=self.delete_btn.center)
        surface.blit(delete_text, delete_rect)