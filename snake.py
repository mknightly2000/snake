import pygame
from pygame import Vector2
from collections import deque


class Snake:
    def __init__(self, game, tile_x, tile_y, initial_size, initial_orientation, color):
        self.game = game
        self.color = color
        self.current_orientation = initial_orientation
        self.next_orientations = deque()
        self.body = deque()
        self.was_moved = False  # Indicates whether the initial snake move was made

        for i in range(initial_size):
            point = Vector2(tile_x, tile_y) + initial_orientation * i
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
            if self.game.game_mode == "Infinite" or self.game.game_mode == "Peaceful":
                if cell_type != "head" and (abs(cell.x - self.body[i + 1].x) > 1 or abs(
                        cell.y - self.body[
                            i + 1].y) > 1):  # keep cell moving towards border if wrapping is happening
                    self._draw_cell(Vector2(self.body[i + 1].x, self.body[i + 1].y), color)
                elif cell_type == "head":
                    extra_x = abs(render_pos.x - cell.x)
                    extra_y = abs(render_pos.y - cell.y)

                    if render_pos.x < 0:
                        self._draw_cell(Vector2(self.game.board_dimensions[0] - extra_x, cell.y), color)
                    elif render_pos.x > self.game.board_dimensions[0] - 1:
                        self._draw_cell(Vector2(-1 + extra_x, cell.y), color)
                    elif render_pos.y < 0:
                        self._draw_cell(Vector2(cell.x, self.game.board_dimensions[1] - extra_y), color)
                    elif render_pos.y > self.game.board_dimensions[1] - 1:
                        self._draw_cell(Vector2(cell.x, -1 + extra_y), color)

            # Fill in corners with snake color
            if cell_type == "corner" or cell_type == "head":
                self._draw_cell(cell, color)

    def _play_orientation_sound(self, orientation):
        if orientation.x == 0 and orientation.y == 1:
            self.game._play_sound("up", 0.4)
        elif orientation.x == 0 and orientation.y == -1:
            self.game._play_sound("down", 0.4)
        elif orientation.x == 1 and orientation.y == 0:
            self.game._play_sound("right", 0.4)
        elif orientation.x == -1 and orientation.y == 0:
            self.game._play_sound("left", 0.4)

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
        if self.game.game_mode == "Infinite" or self.game.game_mode == "Peaceful":
            new_head.x = new_head.x % self.game.board_dimensions[0]
            new_head.y = new_head.y % self.game.board_dimensions[1]
        elif not (0 <= new_head.x < self.game.board_dimensions[0] and 0 <= new_head.y < self.game.board_dimensions[
            1]):
            return False, "border"

        # Handle collision with self
        if self.game.game_mode != "Peaceful":
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
