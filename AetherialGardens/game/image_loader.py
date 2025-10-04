"""game/image_loader.py – File selection and image processing for custom puzzles."""

import os
import tkinter as tk
import tkinter.filedialog
from typing import Optional, Tuple
import pygame
from PIL import Image

# -----------------------------------------------------------------
# Constants
# -----------------------------------------------------------------
MAX_IMAGE_WIDTH = 1920  # Maximum width before downscaling
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp']

class ImageLoader:
    """Handles file selection and image processing for custom puzzles."""
    
    def __init__(self):
        self.selected_image_path: Optional[str] = None
        self.processed_image: Optional[pygame.Surface] = None
        self.original_size: Optional[Tuple[int, int]] = None
        self.processed_size: Optional[Tuple[int, int]] = None
        
    def select_image_file(self) -> bool:
        """
        Open a native OS file dialog to select an image file.
        
        Returns:
            bool: True if a file was selected, False if cancelled or error.
        """
        try:
            # Initialize tkinter root window (hidden)
            root = tk.Tk()
            root.withdraw()
            
            # Set the dialog to open in the user's home directory by default
            initial_dir = os.path.expanduser("~")
            
            # Open file dialog with supported image formats
            file_path = tkinter.filedialog.askopenfilename(
                title="Select an image for your puzzle",
                initialdir=initial_dir,
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.bmp"),
                    ("PNG files", "*.png"),
                    ("JPEG files", "*.jpg *.jpeg"),
                    ("BMP files", "*.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            # Clean up tkinter
            root.destroy()
            
            # Check if a file was selected
            if not file_path:
                return False
                
            # Verify file extension
            _, ext = os.path.splitext(file_path.lower())
            if ext not in SUPPORTED_FORMATS:
                print(f"Unsupported file format: {ext}")
                return False
                
            # Verify file exists
            if not os.path.isfile(file_path):
                print(f"File not found: {file_path}")
                return False
                
            self.selected_image_path = file_path
            return True
            
        except Exception as e:
            print(f"Error selecting file: {e}")
            return False
    
    def load_and_process_image(self) -> bool:
        """
        Load the selected image and process it for use in the game.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        if not self.selected_image_path:
            print("No image file selected")
            return False
            
        try:
            # Load image with PIL for better processing capabilities
            pil_image = Image.open(self.selected_image_path)
            self.original_size = pil_image.size
            
            # Check if image needs downscaling
            if pil_image.width > MAX_IMAGE_WIDTH:
                # Calculate new height maintaining aspect ratio
                aspect_ratio = pil_image.height / pil_image.width
                new_width = MAX_IMAGE_WIDTH
                new_height = int(new_width * aspect_ratio)
                
                # Resize image
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                print(f"Image downscaled from {self.original_size} to ({new_width}, {new_height})")
                
            self.processed_size = pil_image.size
            
            # Convert PIL image to Pygame Surface
            # Convert RGB to RGBA if needed
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
                
            # Convert to Pygame format
            raw_data = pil_image.tobytes()
            size = pil_image.size
            self.processed_image = pygame.image.fromstring(raw_data, size, 'RGBA')
            
            return True
            
        except Exception as e:
            print(f"Error processing image: {e}")
            return False
    
    def get_image_surface(self) -> Optional[pygame.Surface]:
        """Return the processed image as a Pygame Surface."""
        return self.processed_image
    
    def get_original_size(self) -> Optional[Tuple[int, int]]:
        """Return the original image size."""
        return self.original_size
    
    def get_processed_size(self) -> Optional[Tuple[int, int]]:
        """Return the processed image size."""
        return self.processed_size
    
    def reset(self):
        """Reset the loader state."""
        self.selected_image_path = None
        self.processed_image = None
        self.original_size = None
        self.processed_size = None