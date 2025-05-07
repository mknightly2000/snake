import json
import math
import random
import sys
from collections import deque

import pygame
from pygame import Vector2

FPS = 60

pygame.mixer.init()


def center(obj, parent_obj):
    parent_obj_center_x = parent_obj.width / 2
    parent_obj_center_y = parent_obj.height / 2

    x = parent_obj.x + (parent_obj_center_x - obj.width / 2)
    y = parent_obj.y + (parent_obj_center_y - obj.height / 2)

    return x, y


def center_x(obj, x):
    obj = obj.get_rect()
    return x - obj.width / 2


def center_y(obj, y):
    obj = obj.get_rect()
    return y - obj.height / 2


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
        def __init__(self, game, color, x, y):
            self.game = game
            self.color = color
            self.pos = Vector2(x, y)

        def draw(self):
            fruit_rect = pygame.Rect(self.pos.x * game.cell_size, self.pos.y * game.cell_size, game.cell_size,
                                     game.cell_size)
            pygame.draw.rect(self.game.screen, self.color, fruit_rect)

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

        def _draw_cell(self, pos, color):
            """Draw a single cell at the given position."""
            cell_rect = pygame.Rect(
                pos.x * self.game.cell_size,
                pos.y * self.game.cell_size,
                self.game.cell_size,
                self.game.cell_size
            )
            pygame.draw.rect(self.game.screen, color, cell_rect)

        def _calc_cell_orientation(self, cell, cell_index):
            if cell_index == len(self.body) - 1:
                return self.current_orientation

            cell_orientation = self.body[cell_index + 1] - cell

            if cell_orientation.x == 0 and cell_orientation.y == 0:
                return cell_orientation
            else:
                return cell_orientation.normalize()

        def draw(self, interpolation_fraction):
            # create list of colors for each snake cell
            color = self.color
            factor = 0.999
            color_list = []

            for i in range(len(self.body)):
                color_list.append(color)
                color = pygame.Color(int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

            color_list.reverse()

            # draw each cell
            for i, cell in enumerate(self.body):
                color = color_list[i]

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

                cell_orientation = self._calc_cell_orientation(cell, i)
                if cell_type != "head" and (abs(cell.x - self.body[i + 1].x) > 1 or abs(
                        cell.y - self.body[i + 1].y) > 1):  # keep cell moving towards border if wrapping is happening
                    cell_orientation = -cell_orientation

                # Move every cell a bit towards the next cell
                render_pos = cell + interpolation_fraction * cell_orientation

                self._draw_cell(render_pos, color)

                # Make wrapping smooth
                if game.game_mode == "Infinite" or game.game_mode == "Peaceful":
                    if cell_type != "head" and (abs(cell.x - self.body[i + 1].x) > 1 or abs(
                            cell.y - self.body[
                                i + 1].y) > 1):  # keep cell moving towards border if wrapping is happening
                        self._draw_cell(Vector2(self.body[i + 1].x, self.body[i + 1].y), color)
                    elif cell_type == "head":
                        extra_x = abs(render_pos.x - cell.x)
                        extra_y = abs(render_pos.y - cell.y)

                        if render_pos.x < 0:
                            self._draw_cell(Vector2(game.board_dimensions[0] - extra_x, cell.y), color)
                        elif render_pos.x > game.board_dimensions[0] - 1:
                            self._draw_cell(Vector2(-1 + extra_x, cell.y), color)
                        elif render_pos.y < 0:
                            self._draw_cell(Vector2(cell.x, game.board_dimensions[1] - extra_y), color)
                        elif render_pos.y > game.board_dimensions[1] - 1:
                            self._draw_cell(Vector2(cell.x, -1 + extra_y), color)

                # Fill in corners with snake color
                if cell_type == "corner" or cell_type == "head":
                    self._draw_cell(cell, color)

        def _play_orientation_sound(self, orientation):
            if orientation.x == 0 and orientation.y == 1:
                game._play_sound("up", 0.4)
            elif orientation.x == 0 and orientation.y == -1:
                game._play_sound("down", 0.4)
            elif orientation.x == 1 and orientation.y == 0:
                game._play_sound("right", 0.4)
            elif orientation.x == -1 and orientation.y == 0:
                game._play_sound("left", 0.4)

        def orient(self, orientation):
            # Make initial move
            if not self.was_moved:
                if orientation == -self.current_orientation:
                    return

                self.current_orientation = orientation
                self.was_moved = True
                self._play_orientation_sound(orientation)

            # When initial move is completed
            if len(self.next_orientations) == 0:
                if orientation == self.current_orientation or orientation == -self.current_orientation:
                    return
            if len(self.next_orientations) != 0:
                if orientation == self.next_orientations[-1] or orientation == -self.next_orientations[-1]:
                    return

            self.next_orientations.append(orientation)
            self._play_orientation_sound(orientation)

        def move(self):
            new_head = self.body[-1] + self.current_orientation

            # Handle collision with border
            if game.game_mode == "Infinite" or game.game_mode == "Peaceful":
                new_head.x = new_head.x % self.game.board_dimensions[0]
                new_head.y = new_head.y % self.game.board_dimensions[1]
            elif not (0 <= new_head.x < self.game.board_dimensions[0] and 0 <= new_head.y < self.game.board_dimensions[
                1]):
                return False, "border"

            # Handle collision with self
            if game.game_mode != "Peaceful":
                if new_head in list(self.body)[1:]:
                    return False, "self"

            # Update the snake's position by removing the tail and adding a new head in the current direction
            self.body.popleft()
            self.body.append(new_head)
            if len(self.next_orientations) != 0:
                self.current_orientation = self.next_orientations.popleft()

            return True, None

        def grow(self):
            self.body.appendleft(self.body[0].copy())

    def __init__(self):
        # Settings
        self.settings = {
            "board_size" : {"label"          : "Board Size", "options": ["Small", "Medium", "Large", "Extra Large"],
                            "selected_option": "Medium"},
            "snake_color": {"label"          : "Snake Color",
                            "options"        : ["Red", "Blue", "Orange", "Pink", "White", "Black"],
                            "selected_option": "Red"},
            "fruit_color": {"label"          : "Fruit Color", "options": ["Red", "Blue", "Orange", "Purple"],
                            "selected_option": "Purple"},
            "num_fruits" : {"label": "Number of Fruits", "options": ["One", "Two", "Three"], "selected_option": "One"},
            "snake_speed": {"label"          : "Snake Speed", "options": ["Slow", "Moderate", "Fast", "Very Fast"],
                            "selected_option": "Moderate"},
            "game_mode"  : {"label"          : "Game Mode", "options": ["Regular", "Infinite", "Peaceful"],
                            "selected_option": "Regular"},
            "sfx_enabled": {"label": "SFX Enabled", "options": ["Yes", "No"], "selected_option": "Yes"}
        }

        # Suggested cell sizes: 12, 18, 24, and 36
        # LCM(12, 18, 24) = 72
        # Playground dimensions should be multiples of 72.

        self.cell_size = 24  # the width and length of a cell in the board

        self.snake_color = (255, 0, 0)
        self.fruit_color = (184, 130, 238)
        self.num_fruits = 1
        self.snake_speed = 9
        self.game_mode = "Regular"
        self.sfx_enabled = True

        # Params
        self.board_width = 288
        self.board_height = 432
        self.status_bar_height = 70

        self.viewport_width = self.board_width
        self.viewport_height = self.board_height + self.status_bar_height

        board_num_cells_x_direction = self.board_width // self.cell_size
        board_num_cells_y_direction = self.board_height // self.cell_size
        self.board_dimensions = (board_num_cells_x_direction, board_num_cells_y_direction)

        self.font_regular = "fonts/PixelifySans-Regular.ttf"
        self.font_medium = "fonts/PixelifySans-Medium.ttf"
        self.font_semi_bold = "fonts/PixelifySans-SemiBold.ttf"
        self.font_bold = "fonts/PixelifySans-Bold.ttf"

        self.light_grass_color = (165, 207, 82)
        self.dark_grass_color = (155, 193, 77)

        # Scores
        self.game_won = False
        self.score = 0
        self.high_scores = {}

        # Initialize
        self.load_data()
        self.update_game_settings()

        self.screen = pygame.display.set_mode((self.viewport_width, self.viewport_height))
        self.clock = pygame.time.Clock()

        pygame.init()

    def _play_sound(self, sound_name, volume=1.0):
        if not self.sfx_enabled:
            return

        sound = pygame.mixer.Sound(f"sounds/{sound_name}.wav")
        sound.set_volume(volume)
        sound.play()

    def save_data(self):
        data = {
            "settings"   : {setting_key: setting_data["selected_option"] for setting_key, setting_data in
                            self.settings.items()},
            "high_scores": {str(k): v for k, v in self.high_scores.items()}  # Convert frozenset keys to strings
        }

        with open('game_data.json', 'w') as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open('game_data.json', 'r') as f:
                data = json.load(f)
                for setting_key, value in data["settings"].items():
                    self.settings[setting_key]["selected_option"] = value
                self.high_scores = {frozenset(k[12:-2].replace("'", "").split(", ")): v for k, v in
                                    data["high_scores"].items()}
        except (FileNotFoundError, json.JSONDecodeError, KeyError):
            # If file doesn't exist or is invalid, keep default values
            pass

    def update_game_settings(self):
        setting_board_size = self.settings["board_size"]["selected_option"]
        setting_snake_color = self.settings["snake_color"]["selected_option"]
        setting_fruit_color = self.settings["fruit_color"]["selected_option"]
        setting_num_fruits = self.settings["num_fruits"]["selected_option"]
        setting_snake_speed = self.settings["snake_speed"]["selected_option"]
        setting_game_mode = self.settings["game_mode"]["selected_option"]
        setting_sfx_enabled = self.settings["sfx_enabled"]["selected_option"]

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

        # Update snake color
        if setting_snake_color == "Red":
            self.snake_color = (255, 0, 0)
        elif setting_snake_color == "Blue":
            self.snake_color = (0, 0, 255)
        elif setting_snake_color == "Orange":
            self.snake_color = (255, 180, 0)
        elif setting_snake_color == "Pink":
            self.snake_color = (178, 0, 211)
        elif setting_snake_color == "White":
            self.snake_color = (217, 220, 238)
        elif setting_snake_color == "Black":
            self.snake_color = (50, 50, 50)

        # Update fruit color
        if setting_fruit_color == "Red":
            self.fruit_color = (212, 76, 77)
        elif setting_fruit_color == "Blue":
            self.fruit_color = (140, 156, 200)
        elif setting_fruit_color == "Orange":
            self.fruit_color = (208, 125, 0)
        elif setting_fruit_color == "Purple":
            self.fruit_color = (184, 130, 238)

        # Update number of fruits
        if setting_num_fruits == "One":
            self.num_fruits = 1
        elif setting_num_fruits == "Two":
            self.num_fruits = 2
        elif setting_num_fruits == "Three":
            self.num_fruits = 3

        # Update snake speed
        if setting_snake_speed == "Slow":
            self.snake_speed = 6
        elif setting_snake_speed == "Moderate":
            self.snake_speed = 9
        elif setting_snake_speed == "Fast":
            self.snake_speed = 12
        elif setting_snake_speed == "Very Fast":
            self.snake_speed = 15

        # Update game mode
        if setting_game_mode == "Regular":
            self.game_mode = "Regular"
        elif setting_game_mode == "Infinite":
            self.game_mode = "Infinite"
        elif setting_game_mode == "Peaceful":
            self.game_mode = "Peaceful"

        # Update sfx settings
        if setting_sfx_enabled == "Yes":
            self.sfx_enabled = True
        elif setting_sfx_enabled == "No":
            self.sfx_enabled = False

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

    def spawn_fruit(self, snake, existing_fruits):
        all_positions = [(x, y) for x in range(self.board_dimensions[0]) for y in range(self.board_dimensions[1])]
        occupied_positions = set((int(pos.x), int(pos.y)) for pos in snake.body)
        for fruit in existing_fruits:
            occupied_positions.add((int(fruit.pos.x), int(fruit.pos.y)))

        available_positions = [pos for pos in all_positions if pos not in occupied_positions]

        if not available_positions:
            return None

        pos = random.choice(available_positions)
        return self.Fruit(self, self.fruit_color, pos[0], pos[1])

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
                        self._play_sound("select")
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn_rect.collidepoint(event.pos):
                        self._play_sound("select")
                        return "scene_game"
                    elif options_btn_rect.collidepoint(event.pos):
                        self._play_sound("select")
                        return "scene_options_menu"
                    elif exit_btn_rect.collidepoint(event.pos):
                        self._play_sound("select")
                        self.exit_game()

    def options_menu(self):
        title_font = pygame.font.Font(self.font_semi_bold, 35)
        save_font = pygame.font.Font(self.font_bold, 25)
        select_ui_font = pygame.font.Font(self.font_bold, 21)
        label_font = pygame.font.Font(self.font_bold, 15)

        dropdown_width = 200
        dropdown_col_x = (self.viewport_width - dropdown_width) / 2

        menu_title = title_font.render("Options", False, (0, 0, 0))
        save_btn = save_font.render("Save", False, (0, 0, 0))

        menu_title_x = center(menu_title.get_rect(), self.screen.get_rect())[0]
        back_btn_x, back_btn_y = center(save_btn.get_rect(), self.screen.get_rect())
        back_btn_y += 214

        self.screen.fill(self.light_grass_color)

        self.screen.blit(menu_title, (menu_title_x, 20))
        self.screen.blit(save_btn, (back_btn_x, back_btn_y))
        back_btn_rect = save_btn.get_rect(topleft=(back_btn_x, back_btn_y))

        pygame.display.update()

        while True:
            self.clock.tick(FPS)

            select_rects = {}
            for i, (setting_key, setting) in enumerate(self.settings.items()):
                label = setting["label"]
                selected_option = setting["selected_option"]

                select_rect = select_ui(self.screen, dropdown_col_x, 100 + i * 51, selected_option, select_ui_font,
                                        label_font, dropdown_width, label)

                select_rects[setting_key] = select_rect

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self._play_sound("select")
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for setting_key, select_rect in select_rects.items():
                        if select_rect.collidepoint(event.pos):
                            prev_selected_option = self.settings[setting_key]["selected_option"]
                            prev_selected_option_index = self.settings[setting_key]["options"].index(
                                prev_selected_option)
                            new_selected_option_index = (prev_selected_option_index + 1) % len(
                                self.settings[setting_key]["options"])
                            self.settings[setting_key]["selected_option"] = self.settings[setting_key]["options"][
                                new_selected_option_index]

                            self.save_data()
                            self._play_sound("select")
                            break
                    if back_btn_rect.collidepoint(event.pos):
                        self.update_game_settings()
                        self._play_sound("select")
                        return "scene_menu"

            pygame.display.update()

    def game(self):
        self.game_won = False
        snake_x = math.floor(self.board_dimensions[0] * 0.15)
        snake_y = math.floor(self.board_dimensions[1] / 2)
        snake = self.Snake(self, snake_x, snake_y, 4, Vector2(1, 0), self.snake_color)

        fruits = []
        for _ in range(self.num_fruits):
            new_fruit = self.spawn_fruit(snake, fruits)
            fruits.append(new_fruit)

        self.score = 0  # reset score

        snake_move_timer = 0.0  # Time elapsed since the last move
        move_interval = 1 / self.snake_speed  # Move snake every n seconds.

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
                        if game.sfx_enabled:
                            self._play_sound("collision")
                        if reason == "border":
                            print("Game over by collision with map border.")
                        elif reason == "self":
                            print("Game over by collision with self.")

                        return "scene_game_over"

                    # Collision detection with fruits
                    for fruit in fruits[:]:
                        if snake.body[-1] == fruit.pos:
                            fruits.remove(fruit)
                            self.score += 1
                            new_fruit = self.spawn_fruit(snake, fruits)

                            if new_fruit is not None:
                                fruits.append(new_fruit)
                            else:
                                if len(fruits) == 0:
                                    self.game_won = True
                                    self._play_sound("win")
                                    return "scene_game_over"

                            snake.grow()
                            self._play_sound("munching")
                            break

                snake_move_timer -= move_interval  # Subtract the interval to preserve any excess time

            snake_interpolation_fraction = snake_move_timer / move_interval  # A value between 0 and 1, indicating progress towards the next move

            # Drawing
            self.screen.fill(self.light_grass_color)
            self.draw_grass()

            for fruit in fruits:
                fruit.draw()

            if snake.was_moved:
                snake.draw(snake_interpolation_fraction)
            else:
                snake.draw(0)

            self.draw_status_bar()

            pygame.display.update()

    def game_over(self):
        # Save high score
        game_config = frozenset([
            self.settings["board_size"]["selected_option"],
            self.settings["num_fruits"]["selected_option"],
            self.settings["snake_speed"]["selected_option"],
            self.settings["game_mode"]["selected_option"],
        ])

        if game_config in self.high_scores:
            current_high_score = self.high_scores[game_config]
            self.high_scores[game_config] = self.score if self.score > current_high_score else current_high_score
        else:
            self.high_scores[game_config] = self.score

        self.save_data()

        # Display
        title_font = pygame.font.Font(self.font_semi_bold, 35)
        font = pygame.font.Font(self.font_bold, 25)
        smaller_font = pygame.font.Font(self.font_medium, 15)

        menu_title = title_font.render("You Won" if self.game_won else "Game Over", False, (0, 0, 0))
        your_score_title = smaller_font.render("Your Score", False, (255, 255, 255))
        score_value = title_font.render(str(self.score), False, (255, 255, 255))
        high_score_title = smaller_font.render("High Score", False, (255, 255, 255))
        high_score_value = title_font.render(str(self.high_scores[game_config]), False, (255, 255, 255))
        restart_btn = font.render("Restart", False, (0, 0, 0))
        back_btn = font.render("Main Menu", False, (0, 0, 0))

        menu_title_x = center(menu_title.get_rect(), self.screen.get_rect())[0]
        menu_title_y = 20

        left_col_x = 80
        right_col_x = self.viewport_width - left_col_x
        first_row_y = 110
        second_row_y = first_row_y + your_score_title.get_rect().height + 10

        restart_btn_x, restart_btn_y = center(restart_btn.get_rect(), self.screen.get_rect())
        restart_btn_y += (-25 + (second_row_y + score_value.get_rect().height + 25) / 2)
        back_btn_x, back_btn_y = center(back_btn.get_rect(), self.screen.get_rect())
        back_btn_y += (25 + (second_row_y + score_value.get_rect().height + 25) / 2)

        self.screen.fill(self.light_grass_color)

        self.screen.blit(menu_title, (menu_title_x, menu_title_y))

        score_bg = pygame.Rect(0, first_row_y - 25, self.viewport_width,
                               second_row_y + score_value.get_rect().height + 25 - first_row_y + 25)
        pygame.draw.rect(self.screen, (74, 117, 44), score_bg)
        self.screen.blit(your_score_title, (center_x(your_score_title, left_col_x), first_row_y))
        self.screen.blit(score_value, (center_x(score_value, left_col_x), second_row_y))

        self.screen.blit(high_score_title, (center_x(high_score_title, right_col_x), first_row_y))
        self.screen.blit(high_score_value, (center_x(high_score_value, right_col_x), second_row_y))

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
                        self._play_sound("select")
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_btn_rect.collidepoint(event.pos):
                        self._play_sound("select")
                        return "scene_game"
                    elif back_btn_rect.collidepoint(event.pos):
                        self._play_sound("select")
                        return "scene_menu"


if __name__ == "__main__":
    game = Game()
    game.run()
