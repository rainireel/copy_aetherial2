"""game/puzzle.py – minimal sliding‑tile engine (MVP).
Only standard‑library modules + pygame are used.
All logic stays under 150 lines for easy reading/debugging.
"""

import random
from typing import List, Tuple

import pygame

# ------------------------------------------------------------
# Tile – a simple data holder with a pygame.Rect for mouse tests.
# ------------------------------------------------------------
class Tile:
    def __init__(self, number: int, size: int, pos: Tuple[int, int]):
        self.number = number          # 0 = empty slot
        self.size = size
        self.rect = pygame.Rect(pos[0], pos[1], size, size)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.number == 0:
            # Empty slot – just a plain background
            pygame.draw.rect(surface, (15, 40, 25), self.rect)
            return
        # Tile background
        pygame.draw.rect(surface, (70, 150, 100), self.rect)
        # Tile border
        pygame.draw.rect(surface, (30, 80, 60), self.rect, 2)
        # Number (centered)
        txt = font.render(str(self.number), True, (255, 255, 255))
        txt_rect = txt.get_rect(center=self.rect.center)
        surface.blit(txt, txt_rect)


# ------------------------------------------------------------
# Board – holds a 2‑D list of Tiles and implements move logic.
# ------------------------------------------------------------
class Board:
    def __init__(self, rows: int = 3, cols: int = 3, tile_size: int = 150, margin: int = 5):
        self.rows = rows
        self.cols = cols
        self.tile_size = tile_size
        self.margin = margin
        self.tiles: List[List[Tile]] = []
        self.empty_pos = (rows - 1, cols - 1)  # row, col of empty slot
        self._create_tiles()
        self.shuffle(80)  # default scramble depth

    # ------------------- private helpers -------------------
    def _create_tiles(self) -> None:
        """Populate self.tiles with sequential numbers, last slot = 0 (empty)."""
        self.tiles = []
        # Calculate total board size
        board_width = self.cols * (self.tile_size + self.margin) + self.margin
        board_height = self.rows * (self.tile_size + self.margin) + self.margin
        # Calculate offset to center the board in 800x600 window
        offset_x = (800 - board_width) // 2
        offset_y = (600 - board_height) // 2
        
        for r in range(self.rows):
            row: List[Tile] = []
            for c in range(self.cols):
                number = r * self.cols + c + 1
                if (r, c) == (self.rows - 1, self.cols - 1):
                    number = 0
                x = c * (self.tile_size + self.margin) + self.margin + offset_x
                y = r * (self.tile_size + self.margin) + self.margin + offset_y
                row.append(Tile(number, self.tile_size, (x, y)))
            self.tiles.append(row)
        self.empty_pos = (self.rows - 1, self.cols - 1)

    # ------------------- public API -------------------
    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        for row in self.tiles:
            for tile in row:
                tile.draw(surface, font)

    def _swap(self, pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> None:
        r1, c1 = pos_a
        r2, c2 = pos_b
        self.tiles[r1][c1], self.tiles[r2][c2] = self.tiles[r2][c2], self.tiles[r1][c1]
        # Update rect positions so they stay aligned with the grid
        board_width = self.cols * (self.tile_size + self.margin) + self.margin
        board_height = self.rows * (self.tile_size + self.margin) + self.margin
        # Calculate offset to center the board in 800x600 window
        offset_x = (800 - board_width) // 2
        offset_y = (600 - board_height) // 2
        
        tile_a = self.tiles[r1][c1]
        tile_b = self.tiles[r2][c2]
        tile_a.rect.topleft = (
            c1 * (self.tile_size + self.margin) + self.margin + offset_x,
            r1 * (self.tile_size + self.margin) + self.margin + offset_y,
        )
        tile_b.rect.topleft = (
            c2 * (self.tile_size + self.margin) + self.margin + offset_x,
            r2 * (self.tile_size + self.margin) + self.margin + offset_y,
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
        """If a tile adjacent to the empty slot is clicked, slide it."""
        for r, row in enumerate(self.tiles):
            for c, tile in enumerate(row):
                if tile.rect.collidepoint(mouse_pos) and tile.number != 0:
                    if (r, c) in self._neighbors(*self.empty_pos):
                        self._swap((r, c), self.empty_pos)
                        self.empty_pos = (r, c)
                        return

    def shuffle(self, moves: int = 100) -> None:
        """Perform *moves* random legal slides to randomise the board.
        This guarantees a solvable configuration.
        """
        for _ in range(moves):
            er, ec = self.empty_pos
            possible = self._neighbors(er, ec)
            target = random.choice(possible)
            self._swap(self.empty_pos, target)
            self.empty_pos = target

    def is_solved(self) -> bool:
        """Return True if tiles are in sequential order with empty at bottom‑right."""
        for r in range(self.rows):
            for c in range(self.cols):
                expected = r * self.cols + c + 1
                if (r, c) == (self.rows - 1, self.cols - 1):
                    expected = 0
                if self.tiles[r][c].number != expected:
                    return False
        return True