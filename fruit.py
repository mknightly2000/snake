import pygame
from pygame import Vector2


class Fruit:
    def __init__(self, game, tile_x, tile_y, color):
        self.game = game
        self.pos = Vector2(tile_x, tile_y)
        self.color = color

    def draw(self):
        x = self.pos.x * self.game.cell_size
        y = self.pos.y * self.game.cell_size

        fruit_rect = pygame.Rect(x, y, self.game.cell_size, self.game.cell_size)

        pygame.draw.rect(self.game.screen, self.color, fruit_rect)
