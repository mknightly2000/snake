import pygame
from pygame import Vector2


class Fruit:
    def __init__(self, game, color, x, y):
        self.game = game
        self.color = color
        self.pos = Vector2(x, y)

    def draw(self):
        fruit_rect = pygame.Rect(self.pos.x * self.game.cell_size, self.pos.y * self.game.cell_size,
                                 self.game.cell_size, self.game.cell_size)
        pygame.draw.rect(self.game.screen, self.color, fruit_rect)
