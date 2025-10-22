import pygame
import sys

# 1. Initialize Pygame
pygame.init()

# 2. Set up the display
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Pygame Window on macOS")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game loop flag
running = True

# Clock for controlling frame rate
clock = pygame.time.Clock()

# 3. Main game loop
while running:
    # 4. Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Check if the user clicked the close button
            running = False
        # You can add other event handling here (e.g., keyboard presses)
        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_ESCAPE:
        #         running = False

    # 5. Game logic (update game state)
    # For this example, there's no game logic, but this is where it would go.

    # 6. Drawing
    screen.fill(BLACK)  # Fill the screen with black
    # You can draw other elements here, e.g., pygame.draw.circle(screen, WHITE, (400, 300), 50)

    # 7. Update the display
    pygame.display.flip()

    # 8. Control frame rate
    clock.tick(60)  # Limit to 60 frames per second

# 9. Quit Pygame and exit the program
pygame.quit()
sys.exit()
