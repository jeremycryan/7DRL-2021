from ball import Ball, Shelled

import random
import pygame

import constants as c

class OneBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * .8
        self.mass = self.mass * .5
        self.power_boost_factor = 1.5
        self.max_power_reduction = 50
        self.intelligence_mult = .3
        self.load_back_surface()
    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"1_ball.png"))

class TwoBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.power_boost_factor = .9
        self.intelligence_mult = .3
        self.inaccuracy = 3.5
        self.max_power_reduction = 10
    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"2_ball.png"))

class ThreeBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.power_boost_factor = 1.2
        self.max_power_reduction = 70
        self.gravity = 3000000
        self.inaccuracy = 20

        self.intelligence_mult = 1

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"3_ball.png"))

class FourBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.power_boost_factor = 1
        self.intelligence_mult = 1
        self.inaccuracy = 0

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"4_ball.png"))

class FiveBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * 1.35
        self.mass = self.mass * 1.6
        self.power_boost_factor = 1.8
        self.max_power_reduction = 70
        self.drag_constant *= 1

        self.intelligence_mult = .5
        self.inaccuracy = 10

        self.load_back_surface()
    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"5_ball.png"))

class SixBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * 2
        self.mass = self.mass * (self.radius/c.DEFAULT_BALL_RADIUS)**3
        self.power_boost_factor = .8
        self.max_power_reduction = 40

        self.intelligence_mult = 1
        self.inaccuracy = 0

        self.load_back_surface()
    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"5_ball.png"))


class ExampleBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = 90

    def do_things_before_init(self):
        #put code here
        pass