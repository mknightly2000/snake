import sys
from collections import deque

import pygame
from pygame import Vector2

FPS = 60


class Game:
    class Fruit:
        def __init__(self, game, fruit_type, x, y):
            self.game = game
            self.type = "apple"
            self.pos = Vector2(x, y)

        def draw(self):
            fruit_rect = pygame.Rect(self.pos.x * game.cell_size, self.pos.y * game.cell_size, game.cell_size,
                                     game.cell_size)
            pygame.draw.rect(self.game.screen, pygame.Color("Red"), fruit_rect)

    class Snake:
        def __init__(self, game, x, y, initial_size, initial_orientation, color):
            self.game = game
            self.color = color
            self.current_orientation = initial_orientation
            self.next_orientations = deque()
            self.body = deque()

            for i in range(initial_size):
                point = Vector2(x, y) + initial_orientation * i
                self.body.append(point)

        def draw(self, interpolation_fraction):
            for i, cell in enumerate(self.body):
                # Determine the orientation for each segment:
                # - For the head, use the current movement direction
                # - For other segments, use the direction to the next segment
                if i == len(self.body) - 1:
                    cell_orientation = self.current_orientation
                else:
                    cell_orientation = self.body[i + 1] - cell

                # Move every cell a bit towards the next cell
                render_pos = cell + interpolation_fraction * cell_orientation

                body_part_rect = pygame.Rect(
                    render_pos.x * self.game.cell_size,
                    render_pos.y * self.game.cell_size,
                    self.game.cell_size,
                    self.game.cell_size
                )

                pygame.draw.rect(self.game.screen, pygame.Color(self.color), body_part_rect)

        def orient(self, orientation):
            if len(self.next_orientations) == 0:
                if orientation == self.current_orientation or orientation == -self.current_orientation:
                    return
            if len(self.next_orientations) != 0:
                if orientation == self.next_orientations[-1] or orientation == -self.next_orientations[-1]:
                    return

            self.next_orientations.append(orientation)

        def move(self):
            # Update the snake's position by removing the tail and adding a new head in the current direction
            self.body.popleft()
            self.body.append(self.body[-1] + self.current_orientation)
            if len(self.next_orientations) != 0:
                self.current_orientation = self.next_orientations.popleft()

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

        snake = self.Snake(self, 3, 4, 4, Vector2(1, 0), "Red")

        snake_move_timer = 0.0  # Time elapsed since the last move
        move_interval = 0.1  # Move snake every n seconds.

        while True:
            dt = self.clock.tick(FPS) / 1000.0  # Elapsed time since last frame in seconds

            snake_move_timer += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "scene_menu"
                    elif event.key == pygame.K_w or event.key == pygame.K_UP:
                        snake.orient(Vector2(0, -1))
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        snake.orient(Vector2(0, 1))
                    elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                        snake.orient(Vector2(-1, 0))
                    elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        snake.orient(Vector2(1, 0))

            # If enough time has passed, move the snake to the next grid position
            if snake_move_timer >= move_interval:
                snake.move()
                snake_move_timer -= move_interval  # Subtract the interval to preserve any excess time

            snake_interpolation_fraction = snake_move_timer / move_interval  # A value between 0 and 1, indicating progress towards the next move

            # Drawing
            self.screen.fill(self.light_grass_color)
            self.draw_grass()
            snake.draw(snake_interpolation_fraction)

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
