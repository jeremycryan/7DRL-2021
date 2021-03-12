from ball import Ball, Shelled

import random
import pygame

import constants as c

class OneBall(Ball):
    def take_turn(self):
        self.knock(self.cue, random.random()*360, 30)
        self.turn_phase = c.AFTER_HIT

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"1_ball.png"))

