import sys

import pygame
import random

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

        self.in_simulation = False

        self.load_sounds()
        self.current_scene = None
        self.current_scene = LevelScene(self)
        self.main()

    def load_sounds(self):
        self.ball_hit_1a = pygame.mixer.Sound(c.sound_path("balls hit 1(a).wav"))
        self.ball_hit_1b = pygame.mixer.Sound(c.sound_path("balls hit 1(b).wav"))
        self.ball_hit_1c = pygame.mixer.Sound(c.sound_path("balls hit 1(c).wav"))
        self.ball_hit_2a = pygame.mixer.Sound(c.sound_path("balls hit 2(a).wav"))
        self.ball_hit_2b = pygame.mixer.Sound(c.sound_path("balls hit 2(b).wav"))
        self.ball_hit_2c = pygame.mixer.Sound(c.sound_path("balls hit 2(c).wav"))
        self.ball_hit_3a = pygame.mixer.Sound(c.sound_path("balls hit 3(a).wav"))
        self.ball_hit_3b = pygame.mixer.Sound(c.sound_path("balls hit 3(b).wav"))
        self.ball_hit_3c = pygame.mixer.Sound(c.sound_path("balls hit 3(c).wav"))

        self.exploring = pygame.mixer.Sound(c.sound_path("exploring.mp3"))
        self.combat = pygame.mixer.Sound(c.sound_path("combat.mp3"))

    def balls_hit(self, intensity):
        if intensity == 1:
            random.choice([self.ball_hit_3a, self.ball_hit_3b, self.ball_hit_3c]).play()
        elif intensity == 2:
            random.choice([self.ball_hit_1a, self.ball_hit_1b, self.ball_hit_1c]).play()
        elif intensity == 3:
            random.choice([self.ball_hit_2a, self.ball_hit_2b, self.ball_hit_2c]).play()

    def update_global(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        dt = self.clock.tick(c.FPS)/1000
        return dt, events

    def main(self):
        lag = 0
        while True:
            dt, events = self.update_global()
            lag += dt
            while lag > 1/c.SIM_FPS:
                lag -= 1/c.SIM_FPS
                self.current_scene.update(1/c.SIM_FPS, events)
            self.current_scene.draw(self.screen, (0, 0))
            pygame.display.flip()


if __name__ == '__main__':
    Game()