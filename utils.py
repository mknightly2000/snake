import sys
from constants import *
import pygame


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
    title_font = pygame.font.Font(FONT_SEMI_BOLD, 35)
    menu_title = title_font.render(text, False, BLACK)
    menu_title_x = center(menu_title.get_rect(), screen.get_rect())[0]
    screen.blit(menu_title, (menu_title_x, 20))


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
