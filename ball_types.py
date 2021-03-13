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
        self.radius = c.DEFAULT_BALL_RADIUS * 1.25
        self.mass = self.mass * 1.25
        self.power_boost_factor = 1.8
        self.max_power_reduction = 80

        self.intelligence_mult = .5
        self.inaccuracy = 60

        self.till_next_attack = 0
        self.attack_on_room_spawn = True
        # self.game.current_scene.current_ball = self
        # self.game.current_scene.force_player_next = False

        # self.take_turn()

        self.load_back_surface()

    def take_turn(self):
        if (self.till_next_attack > 0):
            #print("NORMAL ATTACK")
            Ball.take_turn(self)
            self.till_next_attack -= 1
        else:
            print("Cast")
            self.till_next_attack = 1
            balls = self.game.current_scene.balls
            for ball in balls:
                if (ball.is_player):
                    continue
                ball.gain_shell()
            self.turn_phase = c.AFTER_HIT

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"7_ball.png"))

class SevenBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * 1.15
        self.mass = self.mass * 1.1
        self.power_boost_factor = 1.4
        self.max_power_reduction = 70

        self.intelligence_mult = .5
        self.inaccuracy = 40

        self.till_next_attack = 0
        self.attack_on_room_spawn = True
        #self.game.current_scene.current_ball = self
        #self.game.current_scene.force_player_next = False

        #self.take_turn()

        self.load_back_surface()
    def take_turn(self):
        if(self.till_next_attack>0):
            print("NORMAL ATTACK")
            Ball.take_turn(self)
            self.till_next_attack -= 1
        else:
            print("Shield")
            self.till_next_attack = 2
            balls = self.game.current_scene.balls
            for ball in balls:
                if(ball.is_player or ball == self):
                    continue
                ball.gain_shell()
            self.turn_phase = c.AFTER_HIT

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"7_ball.png"))

class ExampleBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = 90

    def do_things_before_init(self):
        #put code here
        pass