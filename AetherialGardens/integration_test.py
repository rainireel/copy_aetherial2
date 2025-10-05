"""Integration test for ImageLoader with the existing game modules"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_integration():
    print("Testing ImageLoader integration with game modules...")
    
    # Test importing the ImageLoader
    try:
        from game.image_loader import ImageLoader
        print("✓ Successfully imported ImageLoader from game module")
    except ImportError as e:
        print(f"✗ Failed to import ImageLoader: {e}")
        return False
    
    # Test that ImageLoader can be instantiated
    try:
        loader = ImageLoader()
        print("✓ Successfully instantiated ImageLoader")
    except Exception as e:
        print(f"✗ Failed to instantiate ImageLoader: {e}")
        return False
    
    # Test importing other game modules to make sure we didn't break anything
    try:
        import pygame
        pygame.init()
        print("✓ Successfully imported pygame")
    except ImportError as e:
        print(f"✗ Failed to import pygame: {e}")
        return False
    
    # Test compatibility with puzzle module (if it exists)
    try:
        from game.puzzle import Board
        print("✓ Successfully imported existing game module (Board)")
    except ImportError as e:
        print(f"Note: Board module not found, this may be expected: {e}")
    
    # Test the full functionality with a test image
    test_image_path = os.path.join(os.path.dirname(__file__), 'test_image.png')
    
    if os.path.exists(test_image_path):
        loader.selected_image_path = test_image_path
        
        # Process the image
        if loader.load_and_process_image():
            print("✓ Successfully processed test image")
            
            # Check that we can get the pygame surface
            surface = loader.get_image_surface()
            if surface:
                print("✓ Successfully retrieved pygame surface")
                print(f"  - Surface type: {type(surface)}")
                print(f"  - Surface size: {surface.get_size()}")
            else:
                print("✗ Failed to retrieve pygame surface")
                return False
        else:
            print("✗ Failed to process test image")
            return False
    else:
        print(f"Note: Test image not found at {test_image_path}, skipping processing test")
    
    print("\n✓ All integration tests passed!")
    return True

if __name__ == "__main__":
    test_integration()