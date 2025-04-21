import sys

import pygame

pygame.init()

screen_width = 350
screen_height = 500

pygame.display.set_caption('Snake')
screen = pygame.display.set_mode((screen_width, screen_height))


def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.update()


if __name__ == "__main__":
    main()
