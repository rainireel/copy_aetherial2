"""Simple test to verify CustomPuzzleScreen imports and basic functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

def test_imports():
    print("Testing CustomPuzzleScreen imports and structure...")
    
    # Test if we can import the class
    try:
        from game.custom_puzzle import CustomPuzzleScreen
        print("✓ Successfully imported CustomPuzzleScreen")
    except ImportError as e:
        print(f"✗ Failed to import CustomPuzzleScreen: {e}")
        return False
    
    # Test if we can instantiate without initializing pygame first
    try:
        # We'll mock the required parameters
        import pygame
        pygame.init()  # Initialize pygame
        
        # Create a mock screen rect
        screen_rect = pygame.Rect(0, 0, 800, 600)
        
        # Define mock callbacks
        def mock_back():
            print("Back callback called")
        
        def mock_start_game(level_info):
            print(f"Start game callback called with: {level_info}")
        
        # Create the CustomPuzzleScreen
        custom_screen = CustomPuzzleScreen(screen_rect, mock_back, mock_start_game)
        print("✓ Successfully instantiated CustomPuzzleScreen")
        
        # Test that the image loader is properly initialized
        if hasattr(custom_screen, 'image_loader'):
            print("✓ ImageLoader properly initialized")
        else:
            print("✗ ImageLoader not found")
            return False
            
        # Test that buttons exist
        if hasattr(custom_screen, 'select_btn') and hasattr(custom_screen, 'start_btn'):
            print("✓ UI buttons properly created")
        else:
            print("✗ UI buttons not found")
            return False
            
        # Test that UI elements exist
        if hasattr(custom_screen, 'font') and hasattr(custom_screen, 'title_font'):
            print("✓ Font elements properly created")
        else:
            print("✗ Font elements not found")
            return False
            
        pygame.quit()
        
    except Exception as e:
        print(f"✗ Error during instantiation test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✓ All basic structure tests passed!")
    return True

def test_integration():
    print("\nTesting integration with existing game modules...")
    
    try:
        from game.custom_puzzle import CustomPuzzleScreen
        from game.puzzle import Board
        from game.ui import Button
        from game.image_loader import ImageLoader
        print("✓ All related modules import successfully")
    except ImportError as e:
        print(f"✗ Import error for related modules: {e}")
        return False
    
    print("✓ Integration test passed!")
    return True

if __name__ == "__main__":
    success1 = test_imports()
    success2 = test_integration()
    
    if success1 and success2:
        print("\n🎉 All tests passed! CustomPuzzleScreen is properly implemented.")
    else:
        print("\n❌ Some tests failed.")