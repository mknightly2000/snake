from collections import deque

import pygame
from pygame import Vector2

from constants import *
from utils import play_sound


class Snake:
    """The snake object which is controlled by the player.

    Attributes:
        game: The Game instance this snake belongs to.
        color: The RGB color tuple for the snake's head.
        current_orientation (Vector2): The current movement direction.
        next_orientations (deque): A queue of upcoming direction changes.
        body (deque): List of Vector2 grid positions for snake segments.
        was_moved (bool): Whether the snake has made its initial move.
    """

    def __init__(self, game, tile_x, tile_y, initial_size, initial_orientation, color):
        """Initialize the snake at a grid position with a given size and direction.

        Args:
            game: The Game instance.
            tile_x (int): The starting x-coordinate on the game grid.
            tile_y (int): The starting y-coordinate on the game grid.
            initial_size (int): The initial length of the snake.
            initial_orientation (Vector2): The initial movement direction.
            color: The RGB color tuple for the snake's head.
        """
        self.game = game
        self.color = color
        self.current_orientation = initial_orientation
        self.next_orientations = deque()
        self.body = deque()
        self.was_moved = False

        # Generate the segments of the snake
        for i in range(initial_size):
            point = Vector2(tile_x, tile_y) + initial_orientation * i
            self.body.append(point)

    def _draw_cell(self, pos, color):
        """Draw a single snake segment at the given position.

        Args:
            pos (Vector2): The grid position to draw the cell.
            color: The RGB color tuple for the cell.
        """
        x = pos.x * self.game.cell_size
        y = pos.y * self.game.cell_size

        cell_rect = pygame.Rect(x, y, self.game.cell_size, self.game.cell_size)

        pygame.draw.rect(self.game.screen, color, cell_rect)

    def _generate_color_gradient_list(self):
        """Generate a list of colors for the snake's body gradient.

        Creates a gradient effect by slightly darkening the color for each segment.

        Returns:
            list: A list of RGB color tuples for each snake segment.
        """
        color = self.color
        factor = 0.999
        color_list = []

        for i in range(len(self.body)):
            color_list.append(color)
            color = pygame.Color(int(color[0] * factor), int(color[1] * factor), int(color[2] * factor))

        color_list.reverse()

        return color_list

    def _determine_cell_type(self, i):
        """Determine the type of a snake cell (head, body, corner, or tail).

        Args:
            i (int): The index of the cell in the body deque.

        Returns:
            str: The cell type ("head", "body", "corner", or "tail").
        """
        if i == len(self.body) - 1:
            return "head"
        elif i == 0:
            return "tail"
        else:
            prev_cell = self.body[i - 1]
            next_cell = self.body[i + 1]

            if prev_cell.x != next_cell.x and prev_cell.y != next_cell.y:
                return "corner"
            else:
                return "body"

    def _calc_cell_orientation(self, cell, cell_index):
        """Calculate the orientation of a snake cell.

        Args:
            cell (Vector2): The grid position of the cell.
            cell_index (int): The index of the cell in the body deque.

        Returns:
            Vector2: The orientation vector for the cell.
        """
        if cell_index == len(self.body) - 1:
            return self.current_orientation

        cell_orientation = self.body[cell_index + 1] - cell

        if cell_orientation.x == 0 and cell_orientation.y == 0:
            return cell_orientation
        else:
            return cell_orientation.normalize()

    def _play_orientation_sound(self, orientation):
        """Play a sound effect based on the snake's movement direction.

        Args:
            orientation (Vector2): The movement direction.
        """
        if orientation.x == 0 and orientation.y == 1:
            play_sound(self.game, UP_SOUND, 0.4)
        elif orientation.x == 0 and orientation.y == -1:
            play_sound(self.game, DOWN_SOUND, 0.4)
        elif orientation.x == 1 and orientation.y == 0:
            play_sound(self.game, RIGHT_SOUND, 0.4)
        elif orientation.x == -1 and orientation.y == 0:
            play_sound(self.game, LEFT_SOUND, 0.4)

    def orient(self, orientation):
        """Set the snake's movement direction.

        Ignores invalid moves (reversing direction, and same direction), then queues the direction
        changes. Plays a sound for each valid direction change.

        Args:
            orientation (Vector2): The desired movement direction.
        """
        if not self.was_moved:
            if orientation == -self.current_orientation:
                # Prevent the snake from going backwards
                return

            self.current_orientation = orientation
            self.was_moved = True
            self._play_orientation_sound(orientation)

        # Prevent the snake from moving backwards or registering a forward move by checking the current orientation or the first queued orientation.
        if len(self.next_orientations) == 0:
            if orientation == self.current_orientation or orientation == -self.current_orientation:
                return
        if len(self.next_orientations) != 0:
            if orientation == self.next_orientations[-1] or orientation == -self.next_orientations[-1]:
                return

        self.next_orientations.append(orientation)
        self._play_orientation_sound(orientation)

    def move(self):
        """Move the snake one step in its current direction.

        Checks for collisions with borders or the snake itself based on game mode.
        Updates the snake's position and applies the next queued direction.

        Returns:
            tuple (bool, str or None): the bool indicates whether the move is successful,
                                       and the str indicates the collision type ("border" or "self") if applicable.
        """
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
        """Increase the snake's length by duplicating the tail segment."""
        self.body.appendleft(self.body[0].copy())

    def draw(self, interpolation_fraction):
        """Draw the snake with smooth movement and wrapping effects.

        Uses interpolation for smooth movement and applies a color gradient.
        Handles wrapping in Infinite and Peaceful modes.

        Args:
            interpolation_fraction (float): A value between 0 and 1 indicating the fraction of the step to draw.
        """
        color_list = self._generate_color_gradient_list()

        # Draw each snake segment
        for i, cell in enumerate(self.body):
            color = color_list[i]

            # Determine the orientation for each segment:
            # - For the head, use the current movement direction
            # - For other segments, use the direction to the next segment

            cell_type = self._determine_cell_type(i)

            cell_orientation = self._calc_cell_orientation(cell, i)
            if cell_type != "head" and (abs(cell.x - self.body[i + 1].x) > 1 or abs(
                    cell.y - self.body[i + 1].y) > 1):  # Keep cell moving towards the border if wrapping is happening
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

            # Fill in corners of the snake body with the current segment color to avoid gaps
            if cell_type == "corner" or cell_type == "head":
                self._draw_cell(cell, color)
