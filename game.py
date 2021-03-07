import sys

import pygame

import constants as c


class Game:
    def __init__(self):
        pygame.init()

        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        pygame.display.set_caption(c.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.main()

    def update_global(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        dt = self.clock.tick(c.FPS)
        return dt, events

    def main(self):
        while True:
            dt, events = self.update_global()


if __name__ == '__main__':
    Game()