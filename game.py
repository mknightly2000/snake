import json
import math
import random

from pygame import Vector2

from fruit import Fruit
from snake import Snake
from utils import *


class Game:
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

        self.cell_size = CELL_SIZE_MEDIUM  # the width and length of a cell in the board
        self.snake_color = SNAKE_COLOR_RED
        self.fruit_color = FRUIT_COLOR_PURPLE
        self.num_fruits = 1
        self.snake_speed = SNAKE_SPEED_MODERATE
        self.game_mode = "Regular"
        self.sfx_enabled = True

        # Params
        self.viewport_width = BOARD_WIDTH
        self.viewport_height = BOARD_HEIGHT + STATUS_BAR_HEIGHT

        board_num_cells_x_direction = BOARD_WIDTH // self.cell_size
        board_num_cells_y_direction = BOARD_HEIGHT // self.cell_size
        self.board_dimensions = (board_num_cells_x_direction, board_num_cells_y_direction)

        # Scores
        self.game_won = False
        self.score = 0
        self.high_scores = {}

        # Initialize
        self._load_data()
        self._update_game_settings()

        self.screen = pygame.display.set_mode((self.viewport_width, self.viewport_height))
        self.clock = pygame.time.Clock()

        pygame.mixer.init()

        pygame.init()

    def _save_data(self):
        data = {
            "settings"   : {setting_key: setting_data["selected_option"] for setting_key, setting_data in
                            self.settings.items()},
            "high_scores": {str(k): v for k, v in self.high_scores.items()}  # Convert frozenset keys to strings
        }

        with open('game_data.json', 'w') as f:
            json.dump(data, f)

    def _load_data(self):
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

    def _update_game_settings(self):
        setting_board_size = self.settings["board_size"]["selected_option"]
        setting_snake_color = self.settings["snake_color"]["selected_option"]
        setting_fruit_color = self.settings["fruit_color"]["selected_option"]
        setting_num_fruits = self.settings["num_fruits"]["selected_option"]
        setting_snake_speed = self.settings["snake_speed"]["selected_option"]
        setting_game_mode = self.settings["game_mode"]["selected_option"]
        setting_sfx_enabled = self.settings["sfx_enabled"]["selected_option"]

        # Update board size
        if setting_board_size == "Small":
            self.cell_size = CELL_SIZE_SMALL
        elif setting_board_size == "Medium":
            self.cell_size = CELL_SIZE_MEDIUM
        elif setting_board_size == "Large":
            self.cell_size = CELL_SIZE_LARGE
        elif setting_board_size == "Extra Large":
            self.cell_size = CELL_SIZE_EXTRA_LARGE

        board_num_cells_x_direction = BOARD_WIDTH // self.cell_size
        board_num_cells_y_direction = BOARD_HEIGHT // self.cell_size
        self.board_dimensions = (board_num_cells_x_direction, board_num_cells_y_direction)

        # Update snake color
        if setting_snake_color == "Red":
            self.snake_color = SNAKE_COLOR_RED
        elif setting_snake_color == "Blue":
            self.snake_color = SNAKE_COLOR_BLUE
        elif setting_snake_color == "Orange":
            self.snake_color = SNAKE_COLOR_ORANGE
        elif setting_snake_color == "Pink":
            self.snake_color = SNAKE_COLOR_PINK
        elif setting_snake_color == "White":
            self.snake_color = SNAKE_COLOR_WHITE
        elif setting_snake_color == "Black":
            self.snake_color = SNAKE_COLOR_BLACK

        # Update fruit color
        if setting_fruit_color == "Red":
            self.fruit_color = FRUIT_COLOR_RED
        elif setting_fruit_color == "Blue":
            self.fruit_color = FRUIT_COLOR_BLUE
        elif setting_fruit_color == "Orange":
            self.fruit_color = FRUIT_COLOR_ORANGE
        elif setting_fruit_color == "Purple":
            self.fruit_color = FRUIT_COLOR_PURPLE

        # Update number of fruits
        if setting_num_fruits == "One":
            self.num_fruits = 1
        elif setting_num_fruits == "Two":
            self.num_fruits = 2
        elif setting_num_fruits == "Three":
            self.num_fruits = 3

        # Update snake speed
        if setting_snake_speed == "Slow":
            self.snake_speed = SNAKE_SPEED_SLOW
        elif setting_snake_speed == "Moderate":
            self.snake_speed = SNAKE_SPEED_MODERATE
        elif setting_snake_speed == "Fast":
            self.snake_speed = SNAKE_SPEED_FAST
        elif setting_snake_speed == "Very Fast":
            self.snake_speed = SNAKE_SPEED_VERY_FAST

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

    def _spawn_fruit(self, snake, existing_fruits):
        all_positions = [(x, y) for x in range(self.board_dimensions[0]) for y in range(self.board_dimensions[1])]
        occupied_positions = set((int(pos.x), int(pos.y)) for pos in snake.body)
        for fruit in existing_fruits:
            occupied_positions.add((int(fruit.pos.x), int(fruit.pos.y)))

        available_positions = [pos for pos in all_positions if pos not in occupied_positions]

        if not available_positions:
            return None

        tile_x, tile_y = random.choice(available_positions)
        return Fruit(self, tile_x, tile_y, self.fruit_color)

    def _draw_grass(self):
        for col in range(self.board_dimensions[0]):
            for row in range(self.board_dimensions[1]):
                if (col + row) % 2 == 0:
                    dark_rect = pygame.Rect(col * self.cell_size, row * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, DARK_GRASS_COLOR, dark_rect)

    def _draw_status_bar(self):
        status_bar_rect = pygame.Rect(0, BOARD_HEIGHT, self.viewport_width, STATUS_BAR_HEIGHT)
        pygame.draw.rect(self.screen, UI_COLOR, status_bar_rect)

        font = pygame.font.Font(FONT_FACE_BOLD, 35)
        score_txt = font.render(str(self.score), False, WHITE)
        x, y = center(score_txt.get_rect(), status_bar_rect)

        self.screen.blit(score_txt, (x, y))

    # Scenes
    def _main_menu_scene(self):
        self.screen.fill(LIGHT_GRASS_COLOR)
        render_title(self.screen, "Main Menu")

        btn_font = pygame.font.Font(FONT_FACE_BOLD, 25)

        play_btn_rect = render_centered_text(self.screen, "Play", btn_font, 0, -50, BLACK)
        options_btn_rect = render_centered_text(self.screen, "Options", btn_font, 0, 0, BLACK)
        exit_btn_rect = render_centered_text(self.screen, "Exit", btn_font, 0, +50, BLACK)

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        play_sound(self, SELECT_SOUND)
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn_rect.collidepoint(event.pos):
                        play_sound(self, SELECT_SOUND)
                        return "scene_game"
                    elif options_btn_rect.collidepoint(event.pos):
                        play_sound(self, SELECT_SOUND)
                        return "scene_options_menu"
                    elif exit_btn_rect.collidepoint(event.pos):
                        play_sound(self, SELECT_SOUND)
                        exit_game()

    def _options_menu_scene(self):
        self.screen.fill(LIGHT_GRASS_COLOR)
        render_title(self.screen, "Options")

        btn_font = pygame.font.Font(FONT_FACE_BOLD, 25)
        selected_option_font = pygame.font.Font(FONT_FACE_BOLD, 21)
        label_font = pygame.font.Font(FONT_FACE_BOLD, 15)

        select_btn_width = 200
        select_btn_margin_rl = (self.viewport_width - select_btn_width) / 2

        save_btn_rect = render_centered_text(self.screen, "Save", btn_font, 0, 214, BLACK)

        pygame.display.update()

        while True:
            self.clock.tick(FPS)

            select_btn_rects = {}
            for i, (setting_key, setting) in enumerate(self.settings.items()):
                label = setting["label"]
                selected_option = setting["selected_option"]

                select_btn_rect = render_select_btn(self.screen, select_btn_margin_rl, 100 + i * 51, select_btn_width,
                                                    selected_option, selected_option_font, label, label_font)
                select_btn_rects[setting_key] = select_btn_rect

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        play_sound(self, SELECT_SOUND)
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    for setting_key, select_rect in select_btn_rects.items():
                        if select_rect.collidepoint(event.pos):
                            prev_selected_option = self.settings[setting_key]["selected_option"]
                            prev_selected_option_index = self.settings[setting_key]["options"].index(
                                prev_selected_option)
                            new_selected_option_index = (prev_selected_option_index + 1) % len(
                                self.settings[setting_key]["options"])
                            self.settings[setting_key]["selected_option"] = self.settings[setting_key]["options"][
                                new_selected_option_index]

                            self._save_data()
                            play_sound(self, SELECT_SOUND)
                            break
                    if save_btn_rect.collidepoint(event.pos):
                        self._update_game_settings()
                        play_sound(self, SELECT_SOUND)
                        return "scene_menu"

            pygame.display.update()

    def _game_scene(self):
        self.game_won = False
        snake_x = math.floor(self.board_dimensions[0] * 0.15)
        snake_y = math.floor(self.board_dimensions[1] / 2)
        snake = Snake(self, snake_x, snake_y, 4, Vector2(1, 0), self.snake_color)

        fruits = []
        for _ in range(self.num_fruits):
            new_fruit = self._spawn_fruit(snake, fruits)
            fruits.append(new_fruit)

        self.score = 0  # reset score

        snake_move_timer = 0.0  # Time elapsed since the last move
        move_interval = 1 / self.snake_speed  # Move snake every n seconds.

        while True:
            dt = self.clock.tick(FPS) / 1000.0  # Elapsed time since last frame in seconds

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
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
                        if self.sfx_enabled:
                            play_sound(self, COLLISION_SOUND)
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
                            new_fruit = self._spawn_fruit(snake, fruits)

                            if new_fruit is not None:
                                fruits.append(new_fruit)
                            else:
                                if len(fruits) == 0:
                                    self.game_won = True
                                    play_sound(self, WIN_SOUND)
                                    return "scene_game_over"

                            snake.grow()
                            play_sound(self, MUNCHING_SOUND)
                            break

                snake_move_timer -= move_interval  # Subtract the interval to preserve any excess time

            snake_interpolation_fraction = snake_move_timer / move_interval  # A value between 0 and 1, indicating progress towards the next move

            # Drawing
            self.screen.fill(LIGHT_GRASS_COLOR)
            self._draw_grass()

            for fruit in fruits:
                fruit.draw()

            if snake.was_moved:
                snake.draw(snake_interpolation_fraction)
            else:
                snake.draw(0)

            self._draw_status_bar()

            pygame.display.update()

    def _game_over_scene(self):
        # Save the high score
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

        self._save_data()

        # Display
        self.screen.fill(LIGHT_GRASS_COLOR)
        render_title(self.screen, "You Won" if self.game_won else "Game Over")

        score_title_font = pygame.font.Font(FONT_FACE_MEDIUM, 15)
        score_font = pygame.font.Font(FONT_FACE_SEMI_BOLD, 35)
        btn_font = pygame.font.Font(FONT_FACE_BOLD, 25)

        score_bg_rect_top_y = 85
        score_bg_rect_bottom_y = 205
        score_bg_mid_y = (score_bg_rect_top_y + score_bg_rect_bottom_y) / 2

        score_title_row_y = score_bg_mid_y - 25
        score_value_row_y = score_bg_mid_y + 15

        score_bg_rect = pygame.Rect(0, score_bg_rect_top_y, self.viewport_width,
                                    score_bg_rect_bottom_y - score_bg_rect_top_y)
        pygame.draw.rect(self.screen, UI_COLOR, score_bg_rect)

        render_centered_text(self.screen, "Your Score", score_title_font, -65,
                             score_title_row_y - self.viewport_height / 2, WHITE)
        render_centered_text(self.screen, "High Score", score_title_font, 65,
                             score_title_row_y - self.viewport_height / 2, WHITE)

        render_centered_text(self.screen, str(self.score), score_font, -65,
                             score_value_row_y - self.viewport_height / 2, WHITE)
        render_centered_text(self.screen, str(self.high_scores[game_config]), score_font, 65,
                             score_value_row_y - self.viewport_height / 2, WHITE)

        restart_btn_y_offset = (-25 + score_bg_rect_bottom_y + (
                    self.viewport_height - score_bg_rect_bottom_y) / 2) - self.viewport_height / 2
        restart_btn_rect = render_centered_text(self.screen, "Restart", btn_font, 0, restart_btn_y_offset, BLACK)

        back_btn_y_offset = (25 + score_bg_rect_bottom_y + (
                    self.viewport_height - score_bg_rect_bottom_y) / 2) - self.viewport_height / 2
        back_btn_rect = render_centered_text(self.screen, "Back", btn_font, 0, back_btn_y_offset, BLACK)

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        play_sound(self, SELECT_SOUND)
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_btn_rect.collidepoint(event.pos):
                        play_sound(self, SELECT_SOUND)
                        return "scene_game"
                    elif back_btn_rect.collidepoint(event.pos):
                        play_sound(self, SELECT_SOUND)
                        return "scene_menu"

    def run(self) -> None:
        pygame.display.set_caption("Snake")

        scene = "scene_menu"

        while True:
            if scene == "scene_menu":
                scene = self._main_menu_scene()
            elif scene == "scene_options_menu":
                scene = self._options_menu_scene()
            elif scene == "scene_game":
                scene = self._game_scene()
            elif scene == "scene_game_over":
                scene = self._game_over_scene()
