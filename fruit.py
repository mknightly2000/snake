import pygame
from pygame import Vector2


class Fruit:
    """A fruit object that the snake can eat to grow.

    Attributes:
        game: The Game instance this fruit belongs to.
        pos (Vector2): The grid position (tile_x, tile_y) of the fruit.
        color: The RGB color tuple for rendering the fruit.
    """

    def __init__(self, game, tile_x, tile_y, color):
        """Initialize a fruit at the specified grid position.

        Args:
            game: The Game instance.
            tile_x (int): The x-coordinate on the game grid (column index).
            tile_y (int): The y-coordinate on the game grid (row index).
            color: The RGB color tuple for the fruit.
        """
        self.game = game
        self.pos = Vector2(tile_x, tile_y)
        self.color = color

    def draw(self):
        """Draw the fruit on the game screen.

        Converts the grid position to pixel coordinates and renders a filled rectangle with the fruit's color.
        """
        x = self.pos.x * self.game.cell_size
        y = self.pos.y * self.game.cell_size

        fruit_rect = pygame.Rect(x, y, self.game.cell_size, self.game.cell_size)

        pygame.draw.rect(self.game.screen, self.color, fruit_rect)
