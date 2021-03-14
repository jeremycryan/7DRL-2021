from ball import Ball, Shelled
from particle import BossGravityParticle, GravityParticle, ShieldParticle, HeartBubble, BombBubble, PoofBit

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
        self.power_boost_factor = 1.15
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
        self.power_boost_factor = .7
        self.mass = self.mass * .7
        self.intelligence_mult = .3
        self.inaccuracy = 12
        self.max_power_reduction = 20
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
        self.mass = self.mass * .9
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
        self.mass = self.mass * 1.4
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
        self.mass = self.mass * 1
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
        self.is_ghost = True

    def take_turn(self):
        print("THIS CODE SHOULD NOT RUN SEE GHOST BALL ASAP!!!!!!!!")
        pass

    def do_things_before_init(self):
        # put code here
        pass


    def load_back_surface(self):
        self.back_surface = pygame.image.load(c.image_path(f"8_ball.png"))

class BossBall(Ball):
    def __init__(self, *args, **kwargs):
        self.do_things_before_init()

        self.split = False

        super().__init__(*args, **kwargs)
        self.radius = int(c.DEFAULT_BALL_RADIUS * 2.5)
        self.mass = self.mass * 1.5
        self.power_boost_factor = 1
        self.max_power_reduction = 30
        self.can_have_shield = False
        self.since_blip = 0

        self.intelligence_mult = .5

        if (self.game.current_floor < 3):
            self.inaccuracy = 15
        elif (self.game.current_floor < 4):
            self.inaccuracy = 10
        elif (self.game.current_floor < 5):
            self.inaccuracy = 8
        elif (self.game.current_floor < 6):
            self.inaccuracy = 4
        else:
            self.inaccuracy = 0

        if (self.game.current_floor < 3):
            self.moves_per_turn = 2
        elif(self.game.current_floor<4):
            self.moves_per_turn = 3
        elif(self.game.current_floor<6):
            self.moves_per_turn = 4
        else:
            self.moves_per_turn = 5
        self.did_grav_attack = False
        if (self.game.current_floor < 4):
            self.starting_health = 2
        elif (self.game.current_floor < 5):
            self.starting_health = 3
        else:
            self.starting_health = 4

        self.current_health = self.starting_health
        self.health_balls = []
        self.is_boss = True
        self.can_be_sunk = False
        self.steps_to_reform = 0

        #self.attack_cooldown = False
        self.attack_on_room_spawn = True

        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shadow()
        self.generate_shading()

        #CREATE HEALTH BALLS
        health_ball_count = min(self.game.current_floor, 5)


        for i in range(health_ball_count):
            created_ball = BossHeart(self.game,self.pose.x,self.pose.y)
            self.health_balls.append(created_ball)

    def take_turn(self):


        self.gravity = 0

        balls = copy(self.game.current_scene.balls);
        summon_count = 0
        bomb_count = 0
        heart_count = 0
        for ball in balls:
            if(ball.boss_summoned):
                summon_count += 1
            if(ball.is_bomb):
                bomb_count += 1
            if(ball.is_heart):
                if(ball.sunk):
                    self.health_balls.remove(ball)
                    pass
                else:
                    heart_count += 1

        if(heart_count<= 0 and self.split):
            self.pose = Pose((99999,99999),0)
            self.break_ball()

            balls  = self.game.current_scene.balls
            for ball in balls:
                if(ball.boss_summoned):
                    ball.break_ball()

            self.turn_phase = c.AFTER_HIT
            self.turn_in_progress = True
            return


        if (self.split):
            if(self.steps_to_reform<=0):
                self.reform()
                pass
            self.steps_to_reform -= 1
            self.turn_phase = c.AFTER_HIT
            self.turn_in_progress = True
            return

        self.mass *= 3

        to_room_center = self.pose - Pose((self.game.current_scene.current_room().center()[0], self.game.current_scene.current_room().center()[1]),0)
        if self.game.current_scene.moves_used<self.moves_per_turn-1 and bomb_count<= 0:

            print("BOMB SPAWN")

            spawn_locations = self.game.current_scene.current_room().find_spawn_locations(2)

            if (spawn_locations != False):
                for i in range(0, len(spawn_locations)):
                    self.game.current_scene.particles += [PreBall(self.game, BombBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]

            #self.attack_cooldown = True
            self.turn_phase = c.AFTER_HIT
            self.turn_in_progress = True
        elif self.game.current_scene.moves_used<self.moves_per_turn-1 and to_room_center.magnitude() > 200:#MOVE TO CENTER HERE

            power = min((to_room_center.magnitude()/200)*40, 100)

            self.knock(self.cue, math.degrees(math.atan2(to_room_center.y, -to_room_center.x)), 40)
            self.turn_phase = c.AFTER_HIT
            self.turn_in_progress = True
            pass

        elif self.game.current_scene.moves_used<self.moves_per_turn-1:
            attack_val = random.random()
            print("NORMAL BOSS ATTACK")

            if ((self.pose - self.game.current_scene.player.pose).magnitude()<180):#GRAV PULSE
                self.did_grav_attack
                print("GRAV ATTACK")
                self.gravity = 80000000
                self.end_per_attack()
                pass
            elif (attack_val < .3 and summon_count<= 0):
                spawn_offset = 60

                for ii in range(2):
                    to_player_vect = self.game.current_scene.player.pose - self.pose
                    to_player_vect_ori = to_player_vect.copy()
                    to_player_vect_ori.scale_to(1)

                    if (ii == 0):
                        to_player_vect.rotate_position(15)
                    else:
                        to_player_vect.rotate_position(-15)

                    to_player_vect.scale_to(1)
                    if (self.game.current_floor < 4):
                        created_ball = OneBall(self.game,
                                                 self.pose.x + to_player_vect.x * (self.radius + spawn_offset) + to_player_vect_ori.x*20,
                                                 self.pose.y + to_player_vect.y * (self.radius + spawn_offset) +to_player_vect_ori.y*20)
                    elif (self.game.current_floor < 5):
                        created_ball = TwoBall(self.game,
                                               self.pose.x + to_player_vect.x * (self.radius + spawn_offset) + to_player_vect_ori.x * 20,
                                               self.pose.y + to_player_vect.y * ( self.radius + spawn_offset) + to_player_vect_ori.y * 20)
                    else:
                        created_ball = FiveBall(self.game,
                                               self.pose.x + to_player_vect.x * (self.radius + spawn_offset) + to_player_vect_ori.x * 20,
                                               self.pose.y + to_player_vect.y * ( self.radius + spawn_offset) + to_player_vect_ori.y * 20)
                    created_ball.boss_summoned = True
                    input_ball = copy(created_ball)
                    self.game.current_scene.particles += [PreBall(self.game, input_ball, .8, .4)]
                    input_ball.knock(self.cue, math.degrees(math.atan2(-to_player_vect_ori.y, to_player_vect_ori.x))  , 40)
                if(self.game.current_floor > 3):
                    to_player_vect = self.game.current_scene.player.pose - self.pose
                    to_player_vect_ori = to_player_vect.copy()
                    to_player_vect_ori.scale_to(1)

                    to_player_vect.scale_to(1)
                    created_ball = ThreeBall(self.game,
                                           self.pose.x + to_player_vect.x * (
                                                       self.radius + spawn_offset) + to_player_vect_ori.x * 50,
                                           self.pose.y + to_player_vect.y * (
                                                       self.radius + spawn_offset) + to_player_vect_ori.y * 50)
                    created_ball.boss_summoned = True
                    input_ball = copy(created_ball)
                    self.game.current_scene.particles += [PreBall(self.game, input_ball, .4, .4)]
                    input_ball.knock(self.cue, math.degrees(math.atan2(-to_player_vect_ori.y, to_player_vect_ori.x)) , 50)
                self.end_per_attack()

            elif (attack_val < .25):
                print("WEAK SMASHY ATTACK")
                self.power_boost_factor *= 1.5
                self.mass *= 1.5
                Ball.take_turn(self)
                self.power_boost_factor /= 1.5
                self.mass /= 1.5
            elif (attack_val < .45):
                if(self.game.current_floor>4):
                    print("SMASHY ATTACK")
                    self.power_boost_factor *= 2.5
                    self.mass *= 1.5
                    Ball.take_turn(self)
                    self.power_boost_factor /= 2.5
                    self.mass /= 1.5
                else:
                    print("SMASHY ATTACK")
                    self.power_boost_factor *= 2.5
                    self.mass *= 1.1
                    Ball.take_turn(self)
                    self.power_boost_factor /= 2.5
                    self.mass /= 1.1

            elif(attack_val<.8): #GHOST SHOT CONCINTRATED
                spawn_offset = 90
                for i in range(3):
                    for ii in range(2):
                        to_player_vect = self.game.current_scene.player.pose - self.pose
                        if(ii == 0):
                            to_player_vect.rotate_position(8*i)
                        else:
                            to_player_vect.rotate_position(-8*i)

                        to_player_vect.scale_to(1)
                        created_ball = GhostBall(self.game, self.pose.x + to_player_vect.x * (self.radius + spawn_offset), self.pose.y + to_player_vect.y * (self.radius + spawn_offset))
                        created_ball.mass = .6
                        input_ball = copy(created_ball)
                        self.game.current_scene.particles += [PreBall(self.game,  input_ball, i*.05+.2, .8)]
                        input_ball.knock(self.cue, math.degrees(math.atan2(-to_player_vect.y, to_player_vect.x)) + ((random.random()-.5)*2)*0, 80 )
                self.end_per_attack()

            elif (attack_val < .87):  # GHOST SHOT CONCINTRATED 2nd version
                spawn_offset = 90
                for i in range(1):
                    for ii in range(1):
                        to_player_vect = self.game.current_scene.player.pose - self.pose
                        if (ii == 0):
                            to_player_vect.rotate_position(8 * i)
                        else:
                            to_player_vect.rotate_position(-8 * i)

                        to_player_vect.scale_to(1)
                        created_ball = GhostBall(self.game,
                                                 self.pose.x + to_player_vect.x * (self.radius + spawn_offset),
                                                 self.pose.y + to_player_vect.y * (self.radius + spawn_offset))
                        created_ball.mass = 1
                        created_ball.radius = 35
                        input_ball = copy(created_ball)
                        self.game.current_scene.particles += [PreBall(self.game, input_ball, .6, .3)]
                        input_ball.knock(self.cue, math.degrees(math.atan2(-to_player_vect.y, to_player_vect.x)) + (
                                    (random.random() - .5) * 3) * 0, 100)
                self.end_per_attack()

            else:
                spawn_offset = 70
                for i in range(40):
                    for ii in range(2):
                        to_player_vect = self.game.current_scene.player.pose - self.pose
                        to_player_vect.rotate_position(13 * i + 180 * ii)

                        to_player_vect.scale_to(1)
                        created_ball = GhostBall(self.game,
                                                 self.pose.x + to_player_vect.x * (self.radius + spawn_offset),
                                                 self.pose.y + to_player_vect.y * (self.radius + spawn_offset))
                        created_ball.mass = .6
                        input_ball = copy(created_ball)
                        self.game.current_scene.particles += [PreBall(self.game, input_ball, i * .05 + .2, .8)]
                        input_ball.knock(self.cue, math.degrees(math.atan2(-to_player_vect.y, to_player_vect.x)) + (
                                (random.random() - .5) * 2) * 0, 80)

                self.end_per_attack()
                pass

        elif self.game.current_scene.moves_used>self.moves_per_turn - 1:
            print("FINAL BOSS TURN")
            self.end_per_attack()

        self.mass /= 3
        self.turn_phase = c.AFTER_HIT
        self.turn_in_progress = True
    def end_per_attack(self):
        self.power_boost_factor *= -.1
        Ball.take_turn(self)
        self.power_boost_factor *= -10

    def reform(self):
        #ANIMATION OF SOME KIND (VERSE BALL 7 SHIELDS???)
        balls = copy(self.game.current_scene.balls);
        new_balls = []
        for ball in balls:
            if(not ball.is_heart):
                new_balls.append(ball)
        self.game.current_scene.balls = new_balls

        self.split = False
        self.can_collide = True
        spawn_location = self.game.current_scene.current_room().find_spawn_locations(1)
        self.pose = Pose((spawn_location[0][0], spawn_location[0][1]),0)

        pass
    def do_things_before_init(self):
        # put code here
        pass

    def load_back_surface(self):
        self.back_surface = pygame.image.load(c.image_path(f"8_ball.png"))

    def update(self, dt, events):
        super().update(dt, events)

        if(self.current_health<=0 and not self.split):
            self.split = True
            self.pose = Pose((99999,99999),0)
            self.current_health = self.starting_health
            self.gravity = 0
            self.steps_to_reform = (2*self.moves_per_turn)

            for health_ball in self.health_balls:
                spawn_locations = self.game.current_scene.current_room().find_spawn_locations(1)

                if (spawn_locations != False):
                    health_ball.pose = Pose((spawn_locations[0][0], spawn_locations[0][1]),0)
                    health_ball.x = spawn_locations[0][0]
                    health_ball.y = spawn_locations[0][1]
                    shelled_heart = Shelled(self.game, health_ball)
                    self.game.current_scene.particles += [PreBall(self.game, shelled_heart)]

        if(self.split):
            self.can_collide = False
            self.velocity *= 0

        if not self.game.in_simulation and not self.sunk and self.gravity != 0:
            self.since_blip += dt
            while self.since_blip > 0.002:
                self.since_blip -= 0.002
                self.game.current_scene.particles.append(BossGravityParticle(self.game, self))

    def draw(self, screen, offset=(0, 0)):
        if(not self.split):
            if not self.sunk and self.gravity != 0:
                r = int((c.BOSS_GRAVITY_RADIUS + math.sin(time.time()*12)*3) * (self.scale * 2 - .999))
                pygame.draw.circle(screen, (50, 50, 50), (self.pose.x + offset[0], self.pose.y + offset[1]), r, 1)
            super().draw(screen, offset)

    def generate_shadow(self):
        if not self.split:
            super().generate_shadow()

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

        self.radius = self.radius * 1


        self.power_boost_factor = .8
        self.mass = self.mass * .8
        self.intelligence_mult = .3
        self.inaccuracy = 10
        self.max_power_reduction = 0

        self.heart = pygame.transform.scale(pygame.image.load(c.image_path("heart.png")), (self.radius, self.radius))
        self.behind = pygame.Surface((self.radius*2, self.radius*2))
        self.behind.fill(c.MAGENTA)
        self.behind.set_colorkey(c.MAGENTA)
        pygame.draw.circle(self.behind, (190, 15, 15), (self.radius, self.radius), self.radius)
        self.behind.set_alpha(80)
        self.back_particles = []
        self.since_bubble = 0
        self.is_heart = True


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

class BombBall(Ball):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.radius = self.radius * 1
        self.mass = self.mass * .7
        self.can_be_sunk = False

        self.heart = pygame.transform.scale(pygame.image.load(c.image_path("bomb.png")), (self.radius, self.radius))
        self.behind = pygame.Surface((self.radius*2, self.radius*2))
        self.behind.fill(c.MAGENTA)
        self.behind.set_colorkey(c.MAGENTA)
        pygame.draw.circle(self.behind, (190, 15, 15), (self.radius, self.radius), self.radius)
        self.behind.set_alpha(80)
        self.back_particles = []
        self.since_bubble = 0
        self.is_bomb = True
        self.can_have_shield = False

    def take_turn(self):
        self.turn_phase = c.AFTER_HIT
        self.turn_in_progress = True

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
        balls = self.game.current_scene.balls
        boss_alive = False
        for ball in balls:
            if(ball.is_boss):
                if(ball.split):
                    self.explode_bomb()
                    self.break_ball()
                boss_alive = True

        if(not boss_alive):
            self.break_ball()

        if self.game.in_simulation:
            return

        for particle in self.back_particles:
            particle.update(dt, events)
        for particle in self.back_particles[:]:
            if particle.dead:
                self.back_particles.remove(particle)
        self.since_bubble += dt
        if(self.game.current_scene.player == self.game.current_scene.current_ball):
            if self.since_bubble > 0.03:
                self.since_bubble -= 0.03
                self.back_particles.append(BombBubble(self.game, self))
        else:
            if self.since_bubble > 0.01:
                self.since_bubble -= 0.01
                self.back_particles.append(BombBubble(self.game, self))

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