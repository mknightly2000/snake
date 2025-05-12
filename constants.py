import os
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

FPS = 60

# Colors for the game board and UI
LIGHT_GRASS_COLOR = (165, 207, 82)
DARK_GRASS_COLOR = (155, 193, 77)
UI_COLOR = (74, 117, 44)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

FONT_FACE_REGULAR = resource_path("fonts/PixelifySans-Regular.ttf")
FONT_FACE_MEDIUM = resource_path("fonts/PixelifySans-Medium.ttf")
FONT_FACE_SEMI_BOLD = resource_path("fonts/PixelifySans-SemiBold.ttf")
FONT_FACE_BOLD = resource_path("fonts/PixelifySans-Bold.ttf")

CLICK_SOUND = resource_path("sounds/click.wav")
MUNCHING_SOUND = resource_path("sounds/munching.wav")
COLLISION_SOUND = resource_path("sounds/collision.wav")
WIN_SOUND = resource_path("sounds/win.wav")
UP_SOUND = resource_path("sounds/up.wav")
DOWN_SOUND = resource_path("sounds/down.wav")
RIGHT_SOUND = resource_path("sounds/right.wav")
LEFT_SOUND = resource_path("sounds/left.wav")

# Board dimensions should be multiples of 72.
BOARD_WIDTH = 288
BOARD_HEIGHT = 432
STATUS_BAR_HEIGHT = 70

# Suggested cell sizes: 12, 18, 24, and 36; LCM(12, 18, 24) = 72
CELL_SIZE_SMALL = 36
CELL_SIZE_MEDIUM = 24
CELL_SIZE_LARGE = 18
CELL_SIZE_EXTRA_LARGE = 12

SNAKE_COLOR_RED = (255, 0, 0)
SNAKE_COLOR_BLUE = (0, 0, 255)
SNAKE_COLOR_ORANGE = (255, 180, 0)
SNAKE_COLOR_PINK = (178, 0, 211)
SNAKE_COLOR_WHITE = (217, 220, 238)
SNAKE_COLOR_BLACK = (50, 50, 50)

FRUIT_COLOR_RED = (212, 76, 77)
FRUIT_COLOR_BLUE = (140, 156, 200)
FRUIT_COLOR_ORANGE = (208, 125, 0)
FRUIT_COLOR_PURPLE = (184, 130, 238)

SNAKE_SPEED_SLOW = 6
SNAKE_SPEED_MODERATE = 9
SNAKE_SPEED_FAST = 12
SNAKE_SPEED_VERY_FAST = 15
