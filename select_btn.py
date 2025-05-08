import pygame

from constants import *


class Select_Btn:
    def __init__(self, screen, x, y, width, selected_option, drop_down_font, label=None, label_font=None):
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
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.width = width
        self.selected_option = selected_option
        self.drop_down_font = drop_down_font
        self.label_font = label_font
        self.label = label

        self.selected_text = drop_down_font.render(selected_option, False, WHITE)
        self.height = self.selected_text.get_height()

        self.select_rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def get_select_rect(self):
        return self.select_rect

    def draw(self):
        # Render the dropdown button with the selected option
        pygame.draw.rect(self.screen, (74, 117, 44), self.select_rect)
        self.screen.blit(self.selected_text, (self.x + 10, self.y))

        # Render the triangle
        triangle_center_x = self.x + self.width - 17
        triangle_center_y = self.y + self.height / 2
        triangle_size = 7

        triangle_top_x = triangle_center_x + triangle_size
        triangle_top_y = triangle_center_y
        triangle_left_x = triangle_center_x - triangle_size
        triangle_left_y = triangle_center_y - triangle_size
        triangle_right_x = triangle_center_x - triangle_size
        triangle_right_y = triangle_center_y + triangle_size

        pygame.draw.polygon(self.screen, WHITE, [(triangle_top_x, triangle_top_y), (triangle_left_x, triangle_left_y),
                                                 (triangle_right_x, triangle_right_y)])

        # Render label
        if self.label and self.label_font:
            label_text = self.label_font.render(self.label, False, BLACK)
            label_y = self.y - label_text.get_height()
            self.screen.blit(label_text, (self.x, label_y))
