import sys

import pygame

import constants as c
from level_scene import LevelScene


class Game:
    def __init__(self):
        pygame.init()

        if not c.FULLSCREEN:
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        else:
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE, pygame.FULLSCREEN)

        pygame.display.set_caption(c.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.current_scene = LevelScene(self)
        self.main()

    def update_global(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        dt = self.clock.tick(c.FPS)/1000
        return dt, events

    def main(self):
        while True:
            dt, events = self.update_global()
            self.current_scene.update(dt, events)
            self.current_scene.draw(self.screen, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    Game()