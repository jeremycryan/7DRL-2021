from ball import Ball, Shelled
from particle import GravityParticle, ShieldParticle, HeartBubble, PoofBit

from primitives import Pose

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
        self.radius = int(c.DEFAULT_BALL_RADIUS * .8)
        self.mass = self.mass * .5
        self.power_boost_factor = 1.5
        self.max_power_reduction = 50
        self.intelligence_mult = .3

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shadow()
        self.generate_shading()

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
        self.inaccuracy = 5
        self.max_power_reduction = 10
    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.image.load(c.image_path(f"2_ball.png"))

class FourBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.power_boost_factor = 1.2
        self.max_power_reduction = 70
        self.gravity = 10000000
        self.inaccuracy = 20
        self.since_blip = 0

        self.intelligence_mult = .3

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
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
            pygame.draw.circle(screen, (200, 50, 185), (self.pose.x + offset[0], self.pose.y + offset[1]), r, 1)
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
        self.back_surface = pygame.image.load(c.image_path(f"3_ball.png"))

class FiveBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = int(c.DEFAULT_BALL_RADIUS * 1.35)
        self.mass = self.mass * 1.6
        self.power_boost_factor = 1.8
        self.max_power_reduction = 70
        self.drag_constant *= 1

        self.intelligence_mult = .4
        self.inaccuracy = 10

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shadow()
        self.generate_shading()

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.image.load(c.image_path(f"5_ball.png"))

class SixBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = int(c.DEFAULT_BALL_RADIUS * 1.25)
        self.mass = self.mass * .7
        self.power_boost_factor = 1
        self.max_power_reduction = 30

        self.intelligence_mult = .8
        self.inaccuracy = 8
        self.moves_per_turn = 3

        self.till_next_attack = 1
        # self.game.current_scene.current_ball = self
        # self.game.current_scene.force_player_next = False

        # self.take_turn()

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shadow()
        self.generate_shading()

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
        self.back_surface = pygame.image.load(c.image_path(f"6_ball.png"))

class SevenBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = int(c.DEFAULT_BALL_RADIUS * 1.25)
        self.mass = self.mass * 1.1
        self.power_boost_factor = 1.4
        self.max_power_reduction = 70
        self.can_have_shield = True

        self.intelligence_mult = .4
        self.inaccuracy = 20

        self.till_next_attack = 0
        self.attack_on_room_spawn = True
        #self.game.current_scene.current_ball = self
        #self.game.current_scene.force_player_next = False

        #self.take_turn()
        self.until_next_turn = 0

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shadow()
        self.generate_shading()

    def take_turn(self):
        if(self.till_next_attack>0 or all([isinstance(ball, Shelled) or ball.is_player for ball in self.game.current_scene.balls])):
            print("NORMAL ATTACK")
            Ball.take_turn(self)
            self.till_next_attack -= 1
        else:
            print("Shield")
            self.till_next_attack = 2
            balls = self.game.current_scene.balls
            delay = 0
            self.until_next_turn = 1
            for ball in balls:
                if(ball.is_player or ball.is_boss or not ball.can_have_shield):
                    continue
                if ball.can_have_shield and not isinstance(ball, Shelled):
                    self.give_shell_to(ball, delay=delay)
                    delay += 0.5
            self.until_next_turn += delay

    def update_seven(self, dt, events):
        if self.game.in_simulation:
            return
        self.until_next_turn -= dt

        if not self.turn_in_progress:
            self.until_next_turn = 1
        if self.turn_in_progress and self.turn_phase==c.BEFORE_HIT and self.until_next_turn < 0:
            self.turn_phase = c.AFTER_HIT

    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.image.load(c.image_path(f"7_ball.png"))

    def give_shell_to(self, other, delay=0):
        self.game.current_scene.particles.append(ShieldParticle(self.game, self, other, delay=delay))

class GhostBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = int(c.DEFAULT_BALL_RADIUS * .6)
        self.mass = self.mass * .2
        self.drag_constant = 10
        self.power_boost_factor = 1.5
        self.max_power_reduction = 50
        self.intelligence_mult = .1

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shadow()
        self.generate_shading()

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
        self.back_surface = pygame.image.load(c.image_path(f"8_ball.png"))

class ExampleBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()
        super().__init__(*args, **kwargs)
        self.radius = 90

    def do_things_before_init(self):
        #put code here
        pass


class BossHeart(Ball):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.heart = pygame.transform.scale(pygame.image.load(c.image_path("heart.png")), (self.radius, self.radius))
        self.behind = pygame.Surface((self.radius*2, self.radius*2))
        self.behind.fill(c.MAGENTA)
        self.behind.set_colorkey(c.MAGENTA)
        pygame.draw.circle(self.behind, (190, 15, 15), (self.radius, self.radius), self.radius)
        self.behind.set_alpha(80)
        self.back_particles = []
        self.since_bubble = 0


    def heart_scale(self):
        period = math.pi
        through_period = ((time.time() - self.game.current_scene.music_started) * c.BPM/60 * period) % period
        peak = 2
        growth_factor = peak - 1
        growth = growth_factor * (1 - abs(math.sin(through_period))**0.3)
        return (1.0 + growth_factor*growth) * self.scale

    def load_back_surface(self):
        self.back_surface = pygame.Surface((int(self.radius*2), int(self.radius*2)))
        self.back_surface.fill((200, 200, 230))
        pass

    def process_back_surface(self):
        pass

    def update_even_if_shelled(self, dt, events):
        if self.game.in_simulation:
            return

        for particle in self.back_particles:
            particle.update(dt, events)
        for particle in self.back_particles[:]:
            if particle.dead:
                self.back_particles.remove(particle)
        self.since_bubble += dt
        if self.since_bubble > 0.03:
            self.since_bubble -= 0.03
            self.back_particles.append(HeartBubble(self.game, self))

    def draw(self, screen, offset=(0, 0)):

        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        behind = self.behind
        if self.scale != 1:
            behind = pygame.transform.scale(self.behind, (int(self.radius*2*self.scale), int(self.radius*2*self.scale)))
        screen.blit(behind, (x - behind.get_width()//2, y - behind.get_width()//2))

        for particle in self.back_particles:
            particle.draw(screen, offset=offset)



        d = int(self.radius*self.heart_scale())
        heart = pygame.transform.scale(self.heart, (d, d))
        lag_offset = self.velocity * -0.00
        if lag_offset.magnitude() > self.radius * 0.4:
            lag_offset.scale_to(self.radius*0.2)
        x = self.pose.x + offset[0] - heart.get_width()//2 + lag_offset.x
        y = self.pose.y + offset[1] - heart.get_height()//2 + lag_offset.y
        screen.blit(heart, (x, y))

        screen.blit(self.shading, (self.pose.x + offset[0] - self.shading.get_width()//2, self.pose.y + offset[1] - self.shading.get_height()//2), special_flags=pygame.BLEND_MULT)

        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        pygame.draw.circle(screen, c.BLACK,
                           (x, y),
                           int(self.radius * self.scale) + 1,
                           int(2 * self.alpha / 255))

    def make_poof(self, position, num):
        if self.game.in_simulation:
            return
        for i in range(num):
            smoke = PoofBit(self.game, *position)
            smoke.color = (180, 0, 0)
            self.game.current_scene.floor_particles.append(smoke)