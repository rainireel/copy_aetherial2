"""game/image_loader.py – File selection and image processing for custom puzzles."""

import os
import sys
from typing import Optional, Tuple
import pygame
from PIL import Image

# -----------------------------------------------------------------
# Constants
# -----------------------------------------------------------------
MAX_IMAGE_WIDTH = 1920  # Maximum width before downscaling
SUPPORTED_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp']

def _get_file_dialog_script():
    """Get the file dialog script that avoids pygame/Tkinter conflicts."""
    return """
import os
import sys
try:
    import tkinter as tk
    import tkinter.filedialog
except ImportError:
    print("ERROR: tkinter not available")
    sys.exit(1)

def select_file():
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
        
        if file_path and os.path.isfile(file_path):
            print(file_path.strip())
        else:
            print("CANCELLED")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    select_file()
"""

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
        Uses subprocess to avoid pygame/Tkinter conflicts on macOS.
        
        Returns:
            bool: True if a file was selected, False if cancelled or error.
        """
        try:
            # Import subprocess here to ensure it's available
            import subprocess
            import tempfile
            
            # Use subprocess to run the file dialog in a separate process
            # This avoids the pygame/Tkinter conflict on macOS
            
            # Write the dialog script to a temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(_get_file_dialog_script())
                temp_script = f.name
            
            try:
                # Run the script and capture output
                result = subprocess.run([sys.executable, temp_script], 
                                      capture_output=True, text=True, timeout=60)
                
                # Clean up the temporary script file
                os.unlink(temp_script)
                
                if result.returncode != 0:
                    print(f"File dialog error: {result.stderr}")
                    return False
                
                output = result.stdout.strip()
                
                # Check if user cancelled the dialog
                if output == "CANCELLED" or not output:
                    return False
                
                file_path = output
                
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
                
            except subprocess.TimeoutExpired:
                print("File dialog timed out")
                os.unlink(temp_script)
                return False
            except Exception as e:
                print(f"Error running file dialog: {e}")
                if 'temp_script' in locals():
                    os.unlink(temp_script)
                return False
                
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
            
            # Address "Large Images" best practice: Scale down immediately after loading
            # Check if image needs downscaling for better performance during cropping/puzzle generation
            if pil_image.width > MAX_IMAGE_WIDTH:
                # Calculate new height maintaining aspect ratio
                aspect_ratio = pil_image.height / pil_image.width
                new_width = MAX_IMAGE_WIDTH
                new_height = int(new_width * aspect_ratio)
                
                # Resize image using high-quality LANCZOS filter
                pil_image = pil_image.resize((new_width, new_height), Image.LANCZOS)
                print(f"Large image downscaled from {self.original_size} to ({new_width}, {new_height}) for better performance")
                
            self.processed_size = pil_image.size
            
            # Convert PIL image to Pygame Surface
            # Convert RGB to RGBA if needed
            if pil_image.mode != 'RGBA':
                pil_image = pil_image.convert('RGBA')
                
            # Convert to Pygame format efficiently
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