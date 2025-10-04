"""game/puzzle.py – sliding‑tile engine with optional image tiles."""

import random
from typing import List, Tuple

import pygame

# ------------------------------------------------------------
# Tile – now can optionally hold an image surface.
# ------------------------------------------------------------
class Tile:
    def __init__(
        self,
        number: int,
        size: int,
        pos: Tuple[int, int],
        image: pygame.Surface | None = None,
    ):
        self.number = number          # 0 = empty slot
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1], size, size)
        self.image = image            # None → draw a coloured placeholder

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.number == 0:
            # Empty slot – plain background
            pygame.draw.rect(surface, (15, 40, 25), self.rect)
            return

        if self.image:
            # Blit the image directly (it already fits the tile rect)
            surface.blit(self.image, self.rect.topleft)
        else:
            # Fallback coloured tile
            pygame.draw.rect(surface, (70, 150, 100), self.rect)
            pygame.draw.rect(surface, (30, 80, 60), self.rect, 2)

        # Number overlay (still useful for debugging)
        txt = font.render(str(self.number), True, (255, 255, 255))
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)


# ------------------------------------------------------------
# Board – now accepts an optional image surface to texture the tiles.
# ------------------------------------------------------------
class Board:
    def __init__(
        self,
        rows: int = 3,
        cols: int = 3,
        tile_size: int = 150,
        margin: int = 5,
        image_surface: pygame.Surface | None = None,   # <-- NEW
    ):
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.margin = margin
        self.tiles: List[List[Tile]] = []
        self.empty_pos = (rows - 1, cols - 1)
        self._create_tiles()
        if image_surface:
            self.apply_image(image_surface)   # texture the board
        self.shuffle(80)

    # ------------------- private helpers -------------------
    def _create_tiles(self) -> None:
        """Populate self.tiles with sequential numbers; all tiles start without images."""
        self.tiles = []
        # Calculate total board size to center it in the window
        board_width = self.cols * self.tile_size + (self.cols + 1) * self.margin
        board_height = self.rows * self.tile_size + (self.rows + 1) * self.margin
        # Calculate offset to center the board in the window
        # We'll assume a standard 800x600 window here, but this could be parameterized
        offset_x = (800 - board_width) // 2
        offset_y = (600 - board_height) // 2
        
        for r in range(self.rows):
            row: List[Tile] = []
            for c in range(self.cols):
                number = r * self.cols + c + 1
                if (r, c) == (self.rows - 1, self.cols - 1):
                    number = 0
                x = (c + 1) * self.margin + c * self.tile_size + offset_x
                y = (r + 1) * self.margin + r * self.tile_size + offset_y
                row.append(Tile(number, self.tile_size, (x, y)))
            self.tiles.append(row)
        self.empty_pos = (self.rows - 1, self.cols - 1)

    # -----------------------------------------------------------------
    # Image handling – slice a large image into tile‑sized subsurfaces.
    # -----------------------------------------------------------------
    def apply_image(self, img: pygame.Surface) -> None:
        """
        Scale ``img`` to fit the board (ignoring the outer margin)
        and assign a subsurface to every non‑empty tile.
        """
        # Compute the total drawable area (without margins)
        drawable_w = self.cols * self.tile_size
        drawable_h = self.rows * self.tile_size
        scaled = pygame.transform.smoothscale(img, (drawable_w, drawable_h))

        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                if tile.number == 0:
                    continue  # skip the empty slot
                sub_rect = pygame.Rect(
                    c * self.tile_size,
                    r * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )
                tile.image = scaled.subsurface(sub_rect).copy()

    def apply_custom_image(self, img: pygame.Surface) -> None:
        """
        Apply a custom image to the board tiles.
        This is similar to apply_image but specifically for custom puzzles.
        """
        if not img:
            return
            
        # Compute the total drawable area (without margins)
        drawable_w = self.cols * self.tile_size
        drawable_h = self.rows * self.tile_size
        
        # Scale the image to fit the board
        scaled = pygame.transform.smoothscale(img, (drawable_w, drawable_h))

        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                if tile.number == 0:
                    continue  # skip the empty slot
                sub_rect = pygame.Rect(
                    c * self.tile_size,
                    r * self.tile_size,
                    self.tile_size,
                    self.tile_size,
                )
                tile.image = scaled.subsurface(sub_rect).copy()

    # ------------------- public API -------------------
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for row in self.tiles:
            for tile in row:
                tile.draw(surface, font)

    def _swap(self, pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> None:
        r1, c1 = pos_a
        r2, c2 = pos_b
        self.tiles[r1][c1], self.tiles[r2][c2] = self.tiles[r2][c2], self.tiles[r1][c1]

        # Keep rects aligned with the grid after swapping
        tile_a = self.tiles[r1][c1]
        tile_b = self.tiles[r2][c2]
        offset_x = (800 - (self.cols * self.tile_size + (self.cols + 1) * self.margin)) // 2
        offset_y = (600 - (self.rows * self.tile_size + (self.rows + 1) * self.margin)) // 2
        tile_a.rect.topleft = (
            (c1 + 1) * self.margin + c1 * self.tile_size + offset_x,
            (r1 + 1) * self.margin + r1 * self.tile_size + offset_y,
        )
        tile_b.rect.topleft = (
            (c2 + 1) * self.margin + c2 * self.tile_size + offset_x,
            (r2 + 1) * self.margin + r2 * self.tile_size + offset_y,
        )

    def _neighbors(self, row: int, col: int) -> List[Tuple[int, int]]:
        neigh = []
        if row > 0:
            neigh.append((row - 1, col))
        if row < self.rows - 1:
            neigh.append((row + 1, col))
        if col > 0:
            neigh.append((row, col - 1))
        if col < self.cols - 1:
            neigh.append((row, col + 1))
        return neigh

    def click_at(self, mouse_pos: Tuple[int, int]) -> None:
        for r, row in enumerate(self.tiles):
            for c, tile in enumerate(row):
                if tile.rect.collidepoint(mouse_pos) and tile.number != 0:
                    if (r, c) in self._neighbors(*self.empty_pos):
                        self._swap((r, c), self.empty_pos)
                        self.empty_pos = (r, c)
                        return

    def shuffle(self, moves: int = 100) -> None:
        """Perform *moves* random legal slides – guarantees a solvable board."""
        for _ in range(moves):
            er, ec = self.empty_pos
            possible = self._neighbors(er, ec)
            target = random.choice(possible)
            self._swap(self.empty_pos, target)
            self.empty_pos = target

    def is_solved(self) -> bool:
        """True when tiles are in sequential order with empty slot bottom‑right."""
        for r in range(self.rows):
            for c in range(self.cols):
                expected = r * self.cols + c + 1
                if (r, c) == (self.rows - 1, self.cols - 1):
                    expected = 0
                if self.tiles[r][c].number != expected:
                    return False
        return True
    
    def get_cropped_image(self) -> pygame.Surface:
        """Reconstruct the original cropped image from the tiles."""
        # Create a surface to reconstruct the image
        drawable_w = self.cols * self.tile_size
        drawable_h = self.rows * self.tile_size
        reconstructed = pygame.Surface((drawable_w, drawable_h))
        
        # Copy each tile's image to the reconstructed surface
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.tiles[r][c]
                if tile.number != 0 and tile.image:
                    reconstructed.blit(tile.image, 
                                     (c * self.tile_size, r * self.tile_size))
        
        return reconstructed