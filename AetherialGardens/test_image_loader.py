"""Test script for ImageLoader functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from game.image_loader import ImageLoader

def test_image_loader():
    # Create an ImageLoader instance
    loader = ImageLoader()
    
    print("Testing ImageLoader functionality...")
    
    # Directly set the test image path instead of using file dialog to avoid tkinter conflicts
    test_image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
    
    if os.path.exists(test_image_path):
        print(f"Using test image: {test_image_path}")
        loader.selected_image_path = test_image_path
    else:
        print(f"Test image not found: {test_image_path}")
        return
    
    print("1. Processing the selected image...")
    process_success = loader.load_and_process_image()
    
    if process_success:
        print("Image processed successfully!")
        print(f"Original size: {loader.get_original_size()}")
        print(f"Processed size: {loader.get_processed_size()}")
        
        # Only initialize pygame after the file operations to avoid conflicts
        import pygame
        pygame.init()
        
        # Get the processed image surface
        image_surface = loader.get_image_surface()
        if image_surface:
            print(f"Image surface created: {type(image_surface)}")
            print(f"Surface size: {image_surface.get_size()}")
        pygame.quit()
    else:
        print("Failed to process image")

if __name__ == "__main__":
    test_image_loader()