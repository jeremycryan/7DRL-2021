from ball import Ball, Shelled
from particle import GravityParticle

import random
import pygame
import math
from copy import copy


from particle import PreBall
import constants as c
import time
import math

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

class FourBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.power_boost_factor = 1.2
        self.max_power_reduction = 70
        self.gravity = 3000000
        self.inaccuracy = 20
        self.since_blip = 0

        self.intelligence_mult = .3

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"4_ball.png"))

    def update(self, dt, events):
        super().update(dt, events)
        if not self.game.in_simulation and not self.sunk:
            self.since_blip += dt
            while self.since_blip > 0.005:
                self.since_blip -= 0.005
                self.game.current_scene.particles.append(GravityParticle(self.game, self))

    def draw(self, screen, offset=(0, 0)):
        if not self.sunk:
            r = int((c.GRAVITY_RADIUS + math.sin(time.time()*12)*3) * (self.scale * 2 - .999))
            pygame.draw.circle(screen, (150, 50, 160), (self.pose.x + offset[0], self.pose.y + offset[1]), r, 1)
        super().draw(screen, offset)

class ThreeBall(Ball):
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
        self.back_surface = pygame.image.load(c.image_path(f"3_ball.png"))

class FiveBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * 1.35
        self.mass = self.mass * 1.6
        self.power_boost_factor = 1.8
        self.max_power_reduction = 70
        self.drag_constant *= 1

        self.intelligence_mult = .4
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
        self.mass = self.mass * .7
        self.power_boost_factor = 1
        self.max_power_reduction = 30

        self.intelligence_mult = .4
        self.inaccuracy = 8
        self.moves_per_turn = 3

        self.till_next_attack = 1
        # self.game.current_scene.current_ball = self
        # self.game.current_scene.force_player_next = False

        # self.take_turn()

        self.load_back_surface()

    def take_turn(self):
        if self.game.current_scene.moves_used<1 or (self.game.current_scene.moves_used<2 and (self.game.current_scene.player.pose - self.pose).magnitude() < 200):#(self.till_next_attack > 0):
            print("NORMAL ATTACK")
            Ball.take_turn(self)
            self.turn_phase = c.AFTER_HIT
            self.till_next_attack -= 1
            self.turn_in_progress = True
        elif self.game.current_scene.moves_used<2:
            print("Cast")
            #Ball.take_turn(self)

            #offset = self.current_room().center()

            spawn_offset = 40
            #summoned_balls = []
            for i in range(8):
                to_player_vect = self.game.current_scene.player.pose - self.pose
                to_player_vect.scale_to(1)
                created_ball = GhostBall(self.game, self.pose.x + to_player_vect.x * (self.radius + spawn_offset), self.pose.y + to_player_vect.y * (self.radius + spawn_offset))
                #created_ball = GhostBall(self.game, self.pose.x, self.pose.y)
                input_ball = copy(created_ball)
                #summoned_balls.append(input_ball)
                self.game.current_scene.particles += [PreBall(self.game,  input_ball, i*.025+.2, .4)]
                input_ball.knock(self.cue, math.degrees(math.atan2(-to_player_vect.y, to_player_vect.x)) + ((random.random()-.5)*2)*15, 80 )

            self.till_next_attack = 0
            self.turn_in_progress = True
            self.turn_phase = c.AFTER_HIT
        else:
            print("Turn 3")
            self.power_boost_factor *= .01
            Ball.take_turn(self)
            self.power_boost_factor *= 100

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius * 2, self.radius * 2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"6_ball.png"))

class SevenBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * 1.25
        self.mass = self.mass * 1.1
        self.power_boost_factor = 1.4
        self.max_power_reduction = 70
        self.can_have_shield = False

        self.intelligence_mult = .4
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
                if(ball.is_player or ball == self or ball.is_boss or ball.can_have_shield):
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

class GhostBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = c.DEFAULT_BALL_RADIUS * .6
        self.mass = self.mass * .2
        self.drag_constant = 10
        self.power_boost_factor = 1.5
        self.max_power_reduction = 50
        self.intelligence_mult = .1
        self.load_back_surface()
        self.can_have_shield = False
        self.is_fragile = True
        self.attack_on_room_spawn = False
        self.only_hit_player = True
        self.moves_per_turn = 0

    def take_turn(self):
        print("THIS CODE SHOULD NOT RUN SEE GHOST BALL ASAP!!!!!!!!")
        pass

    def do_things_before_init(self):
        # put code here
        pass


    def load_back_surface(self):
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))
        self.back_surface = pygame.image.load(c.image_path(f"8_ball.png"))

class ExampleBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = 90

    def do_things_before_init(self):
        #put code here
        pass