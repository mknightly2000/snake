import sys

from constants import *


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


def render_title(screen, text):
    title_font = pygame.font.Font(FONT_FACE_SEMI_BOLD, 35)
    menu_title = title_font.render(text, False, BLACK)
    menu_title_x = center(menu_title.get_rect(), screen.get_rect())[0]
    screen.blit(menu_title, (menu_title_x, 20))


def render_centered_text(screen, text, font, px_away_from_center_x, px_away_from_center_y, color):
    btn_surface = font.render(text, False, color)

    x, y = center(btn_surface.get_rect(), screen.get_rect())
    x += px_away_from_center_x
    y += px_away_from_center_y

    screen.blit(btn_surface, (x, y))

    return btn_surface.get_rect(topleft=(x, y))


def render_select_btn(screen, x, y, width, selected_option, selected_option_font, label, label_font):
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
    if not game.sfx_enabled:
        return

    sound = pygame.mixer.Sound(sound_file_name)
    sound.set_volume(volume)
    sound.play()


def exit_game() -> None:
    print("Exiting...")
    pygame.quit()
    sys.exit()
