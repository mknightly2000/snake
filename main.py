import random
import sys
from collections import deque

import pygame
from pygame import Vector2

FPS = 60


# TODO: Fix bug when snake's initial move is towards its tail.

def center(obj, parent_obj):
    parent_obj_center_x = parent_obj.width / 2
    parent_obj_center_y = parent_obj.height / 2

    x = parent_obj.x + (parent_obj_center_x - obj.width / 2)
    y = parent_obj.y + (parent_obj_center_y - obj.height / 2)

    return x, y


def select_ui(screen, x, y, selected_option, drop_down_font, label_font, width, label=None):
    """
    Creates a dropdown component at the specified position and returns its rectangles.

    Parameters:
    - screen: Pygame surface to render on
    - x: X-coordinate of the top-left corner
    - y: Y-coordinate of the top-left corner
    - options: List of strings representing the dropdown options
    - selected_index: Index of the currently selected option
    - is_open: Boolean indicating if the dropdown is expanded
    - drop_down_font: Pygame font object for rendering text
    - label_font: Pygame font object for rendering labels
    - width: Width of the dropdown
    - label: Optional label text

    Returns:
    - dropdown_rect: Pygame Rect of the dropdown button
    """
    # Calculate the maximum width based on the longest option
    selected_text = drop_down_font.render(selected_option, False, (255, 255, 255))
    height = selected_text.get_height()
    select_rect = pygame.Rect(x, y, width, height)

    # Render the dropdown button with the selected option
    pygame.draw.rect(screen, (74, 117, 44), select_rect)
    screen.blit(selected_text, (x + 10, y))

    # Render the triangle
    triangle_center_x = x + width - 17
    triangle_center_y = y + height / 2
    triangle_size = 7

    triangle_top_x = triangle_center_x + triangle_size
    triangle_top_y = triangle_center_y
    triangle_left_x = triangle_center_x - triangle_size
    triangle_left_y = triangle_center_y - triangle_size
    triangle_right_x = triangle_center_x - triangle_size
    triangle_right_y = triangle_center_y + triangle_size

    pygame.draw.polygon(screen, (255, 255, 255), [(triangle_top_x, triangle_top_y), (triangle_left_x, triangle_left_y),
                                                  (triangle_right_x, triangle_right_y)])

    # Render label
    if label:
        label_text = label_font.render(label, False, (0, 0, 0))
        label_y = y - label_text.get_height()
        screen.blit(label_text, (x, label_y))

    return select_rect


class Game:
    class Fruit:
        def __init__(self, game, fruit_type, x, y):
            self.game = game
            self.type = "apple"
            self.pos = Vector2(x, y)

        def draw(self):
            fruit_rect = pygame.Rect(self.pos.x * game.cell_size, self.pos.y * game.cell_size, game.cell_size,
                                     game.cell_size)
            pygame.draw.rect(self.game.screen, pygame.Color(184, 130, 238), fruit_rect)

    class Snake:
        def __init__(self, game, x, y, initial_size, initial_orientation, color):
            self.game = game
            self.color = color
            self.current_orientation = initial_orientation
            self.next_orientations = deque()
            self.body = deque()
            self.was_moved = False  # Indicates if initial snake move was made

            for i in range(initial_size):
                point = Vector2(x, y) + initial_orientation * i
                self.body.append(point)

        def draw(self, interpolation_fraction):
            for i, cell in enumerate(self.body):
                # Determine the orientation for each segment:
                # - For the head, use the current movement direction
                # - For other segments, use the direction to the next segment

                cell_type = None  # "head", "body", "corner", or "tail"

                if i == len(self.body) - 1:
                    cell_type = "head"
                elif i == 0:
                    cell_type = "tail"
                else:
                    prev_cell = self.body[i - 1]
                    next_cell = self.body[i + 1]
                    if prev_cell.x != next_cell.x and prev_cell.y != next_cell.y:
                        cell_type = "corner"
                    else:
                        cell_type = "body"

                if cell_type == "head":
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

                # Fill in corners with snake color
                if cell_type == "corner" or cell_type == "head":
                    corner_rect = pygame.Rect(
                        cell.x * self.game.cell_size,
                        cell.y * self.game.cell_size,
                        self.game.cell_size,
                        self.game.cell_size
                    )
                    pygame.draw.rect(self.game.screen, pygame.Color(self.color), corner_rect)

        def orient(self, orientation):
            # Make initial move
            if not self.was_moved:
                self.current_orientation = orientation
                self.was_moved = True

            # When initial move is completed
            if len(self.next_orientations) == 0:
                if orientation == self.current_orientation or orientation == -self.current_orientation:
                    return
            if len(self.next_orientations) != 0:
                if orientation == self.next_orientations[-1] or orientation == -self.next_orientations[-1]:
                    return

            self.next_orientations.append(orientation)

        def move(self):
            new_head = self.body[-1] + self.current_orientation

            # Check for collisions with border
            if not (0 <= new_head.x < self.game.board_dimensions[0] and 0 <= new_head.y < self.game.board_dimensions[
                1]):
                return False, "border"

            # Check for self-collision with body (excluding the tail)
            if new_head in list(self.body)[1:]:
                return False, "self"

            # Update the snake's position by removing the tail and adding a new head in the current direction
            self.body.popleft()
            self.body.append(new_head)
            if len(self.next_orientations) != 0:
                self.current_orientation = self.next_orientations.popleft()

            return True, None

        def make_initial_move(self, orientation):
            self.current_orientation = orientation
            self.was_moved = True

        def grow(self):
            self.body.appendleft(self.body[0].copy())

    def __init__(self):
        # settings
        self.settings = {
            "board_size" : {"label": "Board Size", "options": ["Small", "Medium", "Large", "Extra Large"], "selected_option": "Medium"},
            "snake_color": {"label": "Snake Color", "options": ["Red", "Green", "Blue"], "selected_option": "Red"},
            "fruit_color": {"label": "Fruit Color", "options": ["Purple", "Black", "White"], "selected_option": "Purple"},
            "num_fruits" : {"label": "Number of Fruits", "options": ["One", "Two", "Three"], "selected_option": "One"},
            "snake_speed": {"label"         : "Snake Speed", "options": ["Slow", "Medium", "Fast", "Very Fast"],
                            "selected_option": "Medium"},
            "game_mode"  : {"label": "Game Mode", "options": ["Regular", "Infinite", "Peaceful"], "selected_option": "Regular"},
        }

        # params
        self.board_width = 288
        self.board_height = 432
        self.status_bar_height = 54

        self.viewport_width = self.board_width
        self.viewport_height = self.board_height + self.status_bar_height

        # Suggested cell sizes: 12, 18, 24, and 36
        # LCM(12, 18, 24) = 72
        # Playground dimensions should be multiples of 72.

        self.cell_size = 24  # the width and length of a cell in the board

        board_num_cells_x_direction = self.board_width // self.cell_size
        board_num_cells_y_direction = self.board_height // self.cell_size
        self.board_dimensions = (board_num_cells_x_direction, board_num_cells_y_direction)

        self.font_regular = "fonts/PixelifySans-Regular.ttf"
        self.font_medium = "fonts/PixelifySans-Medium.ttf"
        self.font_semi_bold = "fonts/PixelifySans-SemiBold.ttf"
        self.font_bold = "fonts/PixelifySans-Bold.ttf"

        self.light_grass_color = (165, 207, 82)
        self.dark_grass_color = (155, 193, 77)

        self.score = 0

        self.screen = pygame.display.set_mode((self.viewport_width, self.viewport_height))
        self.clock = pygame.time.Clock()

        pygame.init()

    def update_game_settings(self):
        setting_board_size = self.settings["board_size"]["selected_option"]
        setting_snake_color = self.settings["snake_color"]["selected_option"]
        setting_fruit_color = self.settings["fruit_color"]["selected_option"]
        setting_num_fruits = self.settings["num_fruits"]["selected_option"]
        setting_snake_speed = self.settings["snake_speed"]["selected_option"]
        setting_game_mode = self.settings["game_mode"]["selected_option"]

        # Update board size
        if setting_board_size == "Small":
            self.cell_size = 36
        elif setting_board_size == "Medium":
            self.cell_size = 24
        elif setting_board_size == "Large":
            self.cell_size = 18
        elif setting_board_size == "Extra Large":
            self.cell_size = 12

        board_num_cells_x_direction = self.board_width // self.cell_size
        board_num_cells_y_direction = self.board_height // self.cell_size
        self.board_dimensions = (board_num_cells_x_direction, board_num_cells_y_direction)

    def run(self) -> None:
        pygame.display.set_caption("Snake")

        scene = "scene_menu"

        while True:
            if scene == "scene_menu":
                scene = self.main_menu()
            elif scene == "scene_options_menu":
                scene = self.options_menu()
            elif scene == "scene_game":
                scene = self.game()
            elif scene == "scene_game_over":
                scene = self.game_over()

    def exit_game(self) -> None:
        print("Exiting...")
        pygame.quit()
        sys.exit()

    def spawn_fruit(self, snake):
        while True:
            x = random.randint(0, self.board_dimensions[0] - 1)
            y = random.randint(0, self.board_dimensions[1] - 1)
            pos = Vector2(x, y)
            if pos not in snake.body:
                return self.Fruit(self, "apple", x, y)

    def draw_grass(self):
        for col in range(self.board_dimensions[0]):
            for row in range(self.board_dimensions[1]):
                if (col + row) % 2 == 0:
                    dark_rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, self.dark_grass_color, dark_rect)

    def draw_status_bar(self):
        status_bar_rect = pygame.Rect(0, self.board_height, self.viewport_width, self.status_bar_height)
        pygame.draw.rect(self.screen, pygame.Color(74, 117, 44), status_bar_rect)

        font = pygame.font.Font(self.font_bold, 35)
        score_txt = font.render(str(self.score), False, (255, 255, 255))
        x, y = center(score_txt.get_rect(), status_bar_rect)

        self.screen.blit(score_txt, (x, y))

    def main_menu(self):
        title_font = pygame.font.Font(self.font_semi_bold, 35)
        font = pygame.font.Font(self.font_bold, 25)

        menu_title = title_font.render("Main Menu", False, (0, 0, 0))
        play_btn = font.render("Play", False, (0, 0, 0))
        options_btn = font.render("Options", False, (0, 0, 0))
        exit_btn = font.render("Exit", False, (0, 0, 0))

        menu_title_x = center(menu_title.get_rect(), self.screen.get_rect())[0]
        play_btn_x, play_btn_y = center(play_btn.get_rect(), self.screen.get_rect())
        play_btn_y -= 50
        options_btn_x, options_btn_y = center(options_btn.get_rect(), self.screen.get_rect())
        exit_btn_x, exit_btn_y = center(exit_btn.get_rect(), self.screen.get_rect())
        exit_btn_y += 50

        self.screen.fill(self.light_grass_color)

        self.screen.blit(menu_title, (menu_title_x, 20))
        self.screen.blit(play_btn, (play_btn_x, play_btn_y))
        self.screen.blit(options_btn, (options_btn_x, options_btn_y))
        self.screen.blit(exit_btn, (exit_btn_x, exit_btn_y))

        play_btn_rect = play_btn.get_rect(topleft=(play_btn_x, play_btn_y))
        options_btn_rect = options_btn.get_rect(topleft=(options_btn_x, options_btn_y))
        exit_btn_rect = exit_btn.get_rect(topleft=(exit_btn_x, exit_btn_y))

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
                    elif options_btn_rect.collidepoint(event.pos):
                        return "scene_options_menu"
                    elif exit_btn_rect.collidepoint(event.pos):
                        self.exit_game()

    def options_menu(self):
        title_font = pygame.font.Font(self.font_semi_bold, 35)
        font = pygame.font.Font(self.font_bold, 25)
        label_font = pygame.font.Font(self.font_bold, 15)

        dropdown_width = 200
        dropdown_col_x = (self.viewport_width - dropdown_width) / 2

        menu_title = title_font.render("Options", False, (0, 0, 0))
        back_btn = font.render("Back", False, (0, 0, 0))

        menu_title_x = center(menu_title.get_rect(), self.screen.get_rect())[0]
        back_btn_x, back_btn_y = center(back_btn.get_rect(), self.screen.get_rect())
        back_btn_y += 200

        self.screen.fill(self.light_grass_color)

        self.screen.blit(menu_title, (menu_title_x, 20))
        self.screen.blit(back_btn, (back_btn_x, back_btn_y))
        back_btn_rect = back_btn.get_rect(topleft=(back_btn_x, back_btn_y))

        pygame.display.update()

        while True:
            self.clock.tick(FPS)

            select_rects = {}
            for i, (setting_key, setting) in enumerate(self.settings.items()):
                label = setting["label"]
                selected_option = setting["selected_option"]

                select_rect = select_ui(self.screen, dropdown_col_x, 100 + i * 55, selected_option, font,
                                        label_font, dropdown_width, label)

                select_rects[setting_key] = select_rect

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for setting_key, select_rect in select_rects.items():
                        if select_rect.collidepoint(event.pos):
                            prev_selected_option = self.settings[setting_key]["selected_option"]
                            prev_selected_option_index = self.settings[setting_key]["options"].index(prev_selected_option)
                            new_selected_option_index = (prev_selected_option_index + 1) % len(self.settings[setting_key]["options"])
                            self.settings[setting_key]["selected_option"] = self.settings[setting_key]["options"][new_selected_option_index]
                            break
                    if back_btn_rect.collidepoint(event.pos):
                        self.update_game_settings()
                        return "scene_menu"

            pygame.display.update()

    def game(self):
        snake = self.Snake(self, 3, 4, 4, Vector2(1, 0), "Red")
        fruit = self.spawn_fruit(snake)

        self.score = 0  # reset score

        snake_move_timer = 0.0  # Time elapsed since the last move
        move_interval = 0.1  # Move snake every n seconds.

        while True:
            dt = self.clock.tick(FPS) / 1000.0  # Elapsed time since last frame in seconds

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

            snake_move_timer += dt
            if not snake.was_moved:
                snake_move_timer = 0

            # If enough time has passed, move the snake to the next grid position
            if snake_move_timer >= move_interval:
                if snake.was_moved:
                    is_snake_move_successful, reason = snake.move()
                    if not is_snake_move_successful:
                        if reason == "border":
                            print("Game over by collision with map border.")
                        elif reason == "self":
                            print("Game over by collision with self.")

                        return "scene_game_over"

                    # Collision detection with fruit
                    elif snake.body[-1] == fruit.pos:
                        fruit = self.spawn_fruit(snake)
                        snake.grow()
                        self.score += 1

                snake_move_timer -= move_interval  # Subtract the interval to preserve any excess time

            snake_interpolation_fraction = snake_move_timer / move_interval  # A value between 0 and 1, indicating progress towards the next move

            # Drawing
            self.screen.fill(self.light_grass_color)
            self.draw_grass()

            fruit.draw()

            if snake.was_moved:
                snake.draw(snake_interpolation_fraction)
            else:
                snake.draw(0)

            self.draw_status_bar()

            pygame.display.update()

    def game_over(self):
        title_font = pygame.font.Font(self.font_semi_bold, 35)
        font = pygame.font.Font(self.font_bold, 25)

        menu_title = title_font.render("Game Over", False, (0, 0, 0))
        restart_btn = font.render("Restart", False, (0, 0, 0))
        back_btn = font.render("Main Menu", False, (0, 0, 0))

        menu_title_x = center(menu_title.get_rect(), self.screen.get_rect())[0]
        restart_btn_x, restart_btn_y = center(restart_btn.get_rect(), self.screen.get_rect())
        restart_btn_y -= 25
        back_btn_x, back_btn_y = center(back_btn.get_rect(), self.screen.get_rect())
        back_btn_y += 25

        self.screen.fill(self.light_grass_color)

        self.screen.blit(menu_title, (menu_title_x, 20))
        self.screen.blit(restart_btn, (restart_btn_x, restart_btn_y))
        self.screen.blit(back_btn, (back_btn_x, back_btn_y))

        restart_btn_rect = restart_btn.get_rect(topleft=(restart_btn_x, restart_btn_y))
        back_btn_rect = back_btn.get_rect(topleft=(back_btn_x, back_btn_y))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_btn_rect.collidepoint(event.pos):
                        return "scene_game"
                    elif back_btn_rect.collidepoint(event.pos):
                        return "scene_menu"


if __name__ == "__main__":
    game = Game()
    game.run()
