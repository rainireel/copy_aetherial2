"""game/utils.py – Utility functions for image processing and tile generation."""

import pygame
from typing import List, Tuple, Optional

def slice_image(source_image: pygame.Surface, grid_size: int) -> List[pygame.Surface]:
    """
    Slice a source image into a grid of tile surfaces.

    Args:
        source_image: The source image to slice
        grid_size: The size of the grid (e.g., 3 for 3x3)

    Returns:
        A list of pygame.Surface objects representing the tiles
    """
    if not source_image or grid_size <= 0:
        return []

    # Get the dimensions of the source image
    img_width, img_height = source_image.get_size()
    
    # Calculate the size of each tile
    tile_width = img_width // grid_size
    tile_height = img_height // grid_size
    
    tiles = []
    
    # Slice the image into tiles
    for row in range(grid_size):
        for col in range(grid_size):
            # Calculate the rectangle for this tile
            tile_rect = pygame.Rect(
                col * tile_width,
                row * tile_height,
                tile_width,
                tile_height
            )
            
            # Extract the tile as a subsurface
            try:
                tile_surface = source_image.subsurface(tile_rect).copy()
                tiles.append(tile_surface)
            except pygame.error:
                # If subsurface fails (e.g., invalid rectangle), create a blank tile
                blank_tile = pygame.Surface((tile_width, tile_height))
                blank_tile.fill((50, 50, 50))  # Gray placeholder
                tiles.append(blank_tile)
    
    # Return all tiles but mark the last one as empty (for sliding puzzle)
    return tiles

def get_cropped_area(surface: pygame.Surface, crop_rect: pygame.Rect) -> Optional[pygame.Surface]:
    """
    Extract a cropped area from a surface.

    Args:
        surface: The source surface
        crop_rect: The rectangle defining the crop area

    Returns:
        A new surface containing the cropped area, or None if invalid
    """
    try:
        # Ensure the crop rectangle is within bounds
        if (crop_rect.left < 0 or crop_rect.top < 0 or
            crop_rect.right > surface.get_width() or 
            crop_rect.bottom > surface.get_height()):
            # Adjust rectangle to fit within surface
            crop_rect = crop_rect.clamp(surface.get_rect())
        
        # Extract and return the cropped area
        cropped = surface.subsurface(crop_rect).copy()
        return cropped
    except pygame.error:
        # Return None if cropping fails
        return None

def create_empty_tile(width: int, height: int, color: Tuple[int, int, int] = (15, 40, 25)) -> pygame.Surface:
    """
    Create an empty/blank tile surface.

    Args:
        width: Width of the tile
        height: Height of the tile
        color: Color for the empty tile (default is dark green used in the game)

    Returns:
        A pygame.Surface representing an empty tile
    """
    empty_tile = pygame.Surface((width, height))
    empty_tile.fill(color)
    return empty_tile

def scale_image_for_performance(image: pygame.Surface, max_dimension: int = 1920) -> pygame.Surface:
    """
    Scale an image down if it exceeds the maximum dimension for performance.

    Args:
        image: The source image to scale
        max_dimension: Maximum allowed dimension (width or height)

    Returns:
        A scaled pygame.Surface, or the original if no scaling was needed
    """
    width, height = image.get_size()
    
    # Address "Large Images" best practice: Scale down large images immediately
    if width > max_dimension or height > max_dimension:
        scale_factor = max_dimension / max(width, height)
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        return pygame.transform.smoothscale(image, (new_width, new_height))
    
    return image