"""Test script for CustomPuzzleScreen functionality"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

import pygame
from game.custom_puzzle import CustomPuzzleScreen

def test_custom_puzzle_screen():
    # Initialize pygame
    pygame.init()
    
    # Create a test window
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Custom Puzzle Screen Test")
    clock = pygame.time.Clock()
    
    # Define callback functions
    def back_callback():
        print("Back button pressed")
        global running
        running = False
    
    def start_game_callback(level_info):
        print(f"Starting game with level info: {level_info}")
        global running
        running = False
    
    # Create the custom puzzle screen
    screen_rect = pygame.Rect(0, 0, 1280, 720)
    custom_screen = CustomPuzzleScreen(screen_rect, back_callback, start_game_callback)
    
    running = True
    while running:
        dt = clock.tick(60)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                custom_screen.handle_event(event)
        
        # Update
        custom_screen.update(dt)
        
        # Draw
        custom_screen.draw(screen)
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    test_custom_puzzle_screen()