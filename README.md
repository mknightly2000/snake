<a name="top"></a>
# Snake Game with Pygame
This is an implementation of the classic Snake game using Python and the Pygame library. It features a graphical interface with customizable settings, multiple game modes, sound effects, and a high-score system.

## Table of Contents
- [Setup](#setup)
- [How to Play](#how-to-play)
- [Code Structure](#code-structure)

## Setup
To run this game, you need Python 3.8 or later.

Once you have Python installed, navigate to the project directory and run the following command to install the required dependencies.

```zsh
pip3 install -r requirements.txt
```

After that, you can start the game by running:

```zsh
python3 main.py
```

## How to Play
When you start the game, you'll see a main menu with the following options: Play, Options, and Exit.
- Play: Starts a new game with the current settings.
- Options: Allows you to customize the game, including:
  - Board Size: Small, Medium, Large, or Extra Large.s
  - Snake Color: Red, Blue, Orange, Pink, White, or Black. 
  - Fruit Color: Red, Blue, Orange, or Purple. 
  - Number of Fruits: One, Two, or Three. 
  - Snake Speed: Slow, Moderate, Fast, or Very Fast. 
  - Game Mode:
    - Regular: Game ends on collision with borders or the snake itself. 
    - Infinite: Snake wraps around the board edges; the game only ends when the snake collides with itself.
    - Peaceful: Snake wraps around edges and cannot collide with itself. 
  - SFX Enabled: Toggle sound effects. 
- Exit: Closes the game.

### Gameplay
- Use the WASD or arrow keys to control the snake's movement direction (up, down, left, right). 
- The objective is to eat fruits to grow longer and increase your score.
- The player winds when the snake grows to fill the entire board.
- On game over, view your score and the high score for the current options configuration.
- Press ESC during gameplay to return to the main menu.

## Code Structure
The game is organized into several Python modules, with the main logic encapsulated in the following classes and files:
- `Game` (`game.py`): Manages the game state, settings, and scenes (main menu, options, gameplay, and game over).
- `Snake` (`snake.py`): Represents the player-controlled snake, handling movement, growth, collision detection, and rendering.
- `Fruit` (`fruit.py`): Represents the fruits the snake eats, managing their position and rendering. 
- `utils.py`: Contains utility functions for rendering text, buttons, and playing sound effects, as well as helper functions for centering objects. 
- `constants.py`: Defines game constants, such as colors, board dimensions, cell sizes, sound file paths, and font file paths.
- `main.py`: Entry point that initializes and runs the `Game` instance.

##
[Back to Top](#top)
