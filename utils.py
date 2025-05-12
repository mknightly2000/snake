import sys
import pygame
from constants import *


def center(obj, parent_obj):
    """Center an object within a parent object.

    Args:
        obj: The object to center.
        parent_obj: The parent object within which to center.

    Returns:
        tuple: The coordinates (x, y) of what the top-left corner of the object should be to center it within the parent.
    """
    parent_obj_center_x = parent_obj.width / 2
    parent_obj_center_y = parent_obj.height / 2

    x = parent_obj.x + (parent_obj_center_x - obj.width / 2)
    y = parent_obj.y + (parent_obj_center_y - obj.height / 2)

    return x, y


def center_x(obj, x):
    """Center an object horizontally at a given x-coordinate.

    Args:
        obj: The object to center.
        x (float): The x-coordinate to center around.

    Returns:
        float: The x-coordinate of what the top-left corner of the object should be for the object to be centered horizontally.
    """
    obj = obj.get_rect()
    return x - obj.width / 2


def center_y(obj, y):
    """Center an object vertically at a given y-coordinate.

    Args:
        obj: The object to center.
        y (float): The y-coordinate to center around.

    Returns:
        float: The y-coordinate of what the top-left corner of the object should be for the object to be centered vertically.
    """
    obj = obj.get_rect()
    return y - obj.height / 2


def render_title(screen, text):
    """Render a title at the top center of the screen.

    Args:
        screen: The Pygame surface to render on.
        text (str): The title text to render.
    """
    title_font = pygame.font.Font(FONT_FACE_SEMI_BOLD, 35)
    menu_title = title_font.render(text, False, BLACK)
    menu_title_x = center(menu_title.get_rect(), screen.get_rect())[0]
    screen.blit(menu_title, (menu_title_x, 20))


def render_centered_text(screen, text, font, px_away_from_center_x, px_away_from_center_y, color):
    """Render text centered on the screen with an offset.

    Args:
        screen: The Pygame surface to render on.
        text (str): The text to render.
        font: The Pygame font object for rendering text.
        px_away_from_center_x (float): Horizontal offset from the screen center.
        px_away_from_center_y (float): Vertical offset from the screen center.
        color: The RGB color tuple for the text.

    Returns:
        pygame.Rect: The rectangle of the rendered text for collision detection.
    """
    btn_surface = font.render(text, False, color)

    x, y = center(btn_surface.get_rect(), screen.get_rect())
    x += px_away_from_center_x
    y += px_away_from_center_y

    screen.blit(btn_surface, (x, y))

    return btn_surface.get_rect(topleft=(x, y))


def render_select_btn(screen, x, y, width, selected_option, selected_option_font, label, label_font):
    """Render a select button with a label and triangle indicator.

    Args:
        screen: The Pygame surface to render on.
        x (float): The x-coordinate of the top-left corner.
        y (float): The y-coordinate of the top-left corner.
        width (float): The width of the dropdown button.
        selected_option (str): The currently selected option to display.
        selected_option_font: The Pygame font object for the selected option text.
        label (str): The label text for the button, which would be displayed on top of it.
        label_font: The Pygame font object for the label text.

    Returns:
        pygame.Rect: The rectangle of the dropdown button for collision detection.
    """
    selected_text = selected_option_font.render(selected_option, False, WHITE)
    height = selected_text.get_height()
    select_rect = pygame.Rect(x, y, width, height)

    # Render the dropdown button with the selected option
    pygame.draw.rect(screen, UI_COLOR, select_rect)
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

    pygame.draw.polygon(screen, WHITE, [(triangle_top_x, triangle_top_y), (triangle_left_x, triangle_left_y),
                                             (triangle_right_x, triangle_right_y)])

    # Render label
    if label and label_font:
        label_text = label_font.render(label, False, BLACK)
        label_y = y - label_text.get_height()
        screen.blit(label_text, (x, label_y))

    return select_rect


def play_sound(game, sound_file_name, volume=1.0):
    """Play a sound effect if sound is enabled.

    Args:
        game: The Game instance containing sound settings.
        sound_file_name (str): The path to the sound file.
        volume (float): The volume level (0.0 to 1.0).
    """
    if not game.sfx_enabled:
        return

    sound = pygame.mixer.Sound(sound_file_name)
    sound.set_volume(volume)
    sound.play()


def exit_game() -> None:
    """
    Prints an exit message, quits Pygame, and terminates the program.
    """
    print("Exiting...")
    pygame.quit()
    sys.exit()
