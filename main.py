import sys

import pygame
from pygame import Vector2
from collections import deque


class Game:
    class Fruit:
        def __init__(self, game, fruit_type, x, y):
            self.game = game
            self.type = "apple"
            self.pos = pygame.Vector2(x, y)

        def draw(self):
            fruit_rect = pygame.Rect(self.pos.x * game.cell_size, self.pos.y * game.cell_size, game.cell_size,
                                     game.cell_size)
            pygame.draw.rect(self.game.screen, pygame.Color("Red"), fruit_rect)

    class Snake:
        def __init__(self, game, x, y, initial_size, initial_orientation, color):
            self.game = game
            self.color = color
            self.current_orientation = initial_orientation
            self.body = deque()

            for i in range(initial_size):
                point = Vector2(x, y) + initial_orientation * i
                self.body.append(point)

        def draw(self):
            for cell in self.body:
                body_part_rect = pygame.Rect(cell.x * game.cell_size, cell.y * game.cell_size, game.cell_size,
                                             game.cell_size)

                pygame.draw.rect(self.game.screen, pygame.Color(self.color), body_part_rect)

        def move(self):
            self.body.popleft()
            self.body.append(self.body[-1] + self.current_orientation)


    def __init__(self):
        self.menu_screen_width = 350
        self.menu_screen_height = 500

        self.screen = pygame.display.set_mode((self.menu_screen_width, self.menu_screen_height))

        self.cell_size = 25  # the width and length of a cell in the board
        self.board_dimensions = (14, 20)
        self.game_screen_width = self.cell_size * self.board_dimensions[0]
        self.game_screen_height = self.cell_size * self.board_dimensions[1]

        self.font_semi_bold = "fonts/PixelifySans-SemiBold.ttf"
        self.light_grass_color = (165, 207, 82)
        self.dark_grass_color = (155, 193, 77)

        self.clock = pygame.time.Clock()

        pygame.init()

    def run(self) -> None:
        pygame.display.set_caption("Snake")

        scene = "scene_menu"

        while True:
            if scene == "scene_menu":
                scene = self.menu()
            elif scene == "scene_game":
                scene = self.game()

    def exit_game(self) -> None:
        print("Exiting...")
        pygame.quit()
        sys.exit()

    def draw_grass(self):
        dark_rect = pygame.Rect(1, 2, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, self.dark_grass_color, dark_rect)
        for col in range(self.board_dimensions[0]):
            for row in range(self.board_dimensions[1]):
                if (col + row) % 2 == 0:
                    dark_rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, self.dark_grass_color, dark_rect)

    def menu(self):
        self.screen = pygame.display.set_mode((self.menu_screen_width, self.menu_screen_height))

        font = pygame.font.Font(self.font_semi_bold, 35)

        menu_title = font.render("Main Menu", False, (0, 0, 0))
        play_btn = font.render("Play", False, (0, 0, 0))
        exit_btn = font.render("Exit", False, (0, 0, 0))

        self.screen.fill(self.light_grass_color)

        self.screen.blit(menu_title, (10, 5))
        self.screen.blit(play_btn, (10, 80))
        play_btn_rect = play_btn.get_rect(topleft=(10, 80))
        self.screen.blit(exit_btn, (10, 120))
        exit_btn_rect = exit_btn.get_rect(topleft=(10, 120))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn_rect.collidepoint(event.pos):
                        return "scene_game"
                    elif exit_btn_rect.collidepoint(event.pos):
                        self.exit_game()

    def game(self):
        self.screen = pygame.display.set_mode((self.game_screen_width, self.game_screen_height))

        self.screen.fill(self.light_grass_color)
        self.draw_grass()

        self.Snake(game, 3, 4, 4, Vector2(1, 0), "Red").draw()

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "scene_menu"


            pygame.display.update()
            self.clock.tick(60)

if __name__ == "__main__":
    game = Game()
    game.run()
