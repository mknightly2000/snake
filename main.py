import sys

import pygame


class Game:

    def __init__(self):
        self.menu_screen_width = 350
        self.menu_screen_height = 500

        self.cell_size = 25  # the width and length of a cell in the board
        self.board_dimensions = (14, 20)
        self.game_screen_width = self.cell_size * self.board_dimensions[0]
        self.game_screen_height = self.cell_size * self.board_dimensions[1]

        self.font_semi_bold = "fonts/PixelifySans-SemiBold.ttf"
        self.background_color = (64, 197, 91)

        pygame.init()

    def run(self) -> None:
        pygame.display.set_caption("Snake")

        scene = "scene_menu"

        while True:
            if scene == "scene_menu":
                scene = self.menu()
            elif scene == "scene_game":
                scene = self.game()

    def exit_game(self) -> None:
        print("Exiting...")
        pygame.quit()
        sys.exit()

    def menu(self):
        screen = pygame.display.set_mode((self.menu_screen_width, self.menu_screen_height))

        font = pygame.font.Font(self.font_semi_bold, 35)

        menu_title = font.render("Main Menu", False, (0, 0, 0))
        play_btn = font.render("Play", False, (0, 0, 0))
        exit_btn = font.render("Exit", False, (0, 0, 0))

        screen.fill(self.background_color)

        screen.blit(menu_title, (10, 5))
        screen.blit(play_btn, (10, 80))
        play_btn_rect = play_btn.get_rect(topleft=(10, 80))
        screen.blit(exit_btn, (10, 120))
        exit_btn_rect = exit_btn.get_rect(topleft=(10, 120))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        return "scene_game"
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if play_btn_rect.collidepoint(event.pos):
                        return "scene_game"
                    elif exit_btn_rect.collidepoint(event.pos):
                        self.exit_game()

    def game(self):
        screen = pygame.display.set_mode((self.game_screen_width, self.game_screen_height))
        font = pygame.font.Font(self.font_semi_bold, 35)

        menu_txt = font.render("Game running...", False, (0, 0, 0))

        screen.fill(self.background_color)

        screen.blit(menu_txt, (10, 5))

        pygame.display.update()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit_game()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "scene_menu"


if __name__ == "__main__":
    game = Game()
    game.run()
