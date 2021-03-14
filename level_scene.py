from scene import Scene
from ball import Ball, Shelled
from player import Player
from map import Map
from camera import Camera
import pygame
import constants as c
from ball_types import *
from particle import PreBall, ShieldParticle


class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.map = Map(self.game)
        self.player = Player(game, *self.map.player_spawn())
        self.balls = [self.player]
                      #Ball(self.game, 300, 250)]
                      # Ball(self.game, 400, 200, 50),
                      # Ball(self.game, 550, 150),
                      # Shelled(self.game, Ball(self.game), x=500, y=500)]
        self.current_ball = self.player
        self.current_ball.turn_in_progress = True
        self.particles = []
        self.floor_particles = []
        self.camera = Camera(game, self.current_room())
        self.force_player_next = False
        self.game.exploring.play(-1)
        self.game.combat.play(-1)
        self.music_started = time.time()
        self.game.combat.set_volume(0)
        self.moves_used = 0
        self.boss_is_dead = False

    def shake(self, amt, pose=None):
        if not self.game.in_simulation:
            self.camera.shake(amt, pose)

    def update_current_ball(self):
        if self.balls_are_spawning() or self.shields_are_spawning():
            return
        if not self.current_ball.turn_in_progress or self.current_ball.sunk:
            priority = list(self.priority_balls())
            if priority:
                self.current_ball = priority.pop()
                self.current_ball.attack_on_room_spawn = False
            elif self.force_player_next and not self.player.sunk:
                self.current_ball = self.player
                self.force_player_next = False
            else:
                self.moves_used += 1
                if(self.current_ball.moves_per_turn <= self.moves_used):
                    self.moves_used = 0
                    print("NEXT BALL")
                    balls_no_ghosts = []
                    for ball in self.balls:
                        if(ball.moves_per_turn != 0):
                            balls_no_ghosts.append(ball)
                    if(len(balls_no_ghosts)!= 0):
                        index = (self.balls.index(self.current_ball) + 1) % len(self.balls)
                        self.current_ball = self.balls[index]
                    else:
                        copyed_ghosts = copy(balls_no_ghosts)
                        index = (copyed_ghosts.index(self.current_ball) + 1) % len(self.balls)
                        self.current_ball = copyed_ghosts[index]
                        
                #else:
                   # self.current_ball.turn_in_progress = False


            self.current_ball.start_turn()

    def priority_balls(self):
        for ball in self.balls:
            if ball.attack_on_room_spawn:
                yield ball

    def no_enemies(self):
        if self.balls_are_spawning():
            return False
        for ball in self.balls:
            if ball is not self.player:
                return False
        return True

    def all_balls_below_speed(self, speed=5):
        for ball in self.balls:
            if ball.velocity.magnitude() > speed:
                return False
        return True

    def update(self, dt, events):
        if self.current_room().is_boss_room:
            self.boss_is_dead = True

        for ball in self.balls:
            ball._did_collide = False;
        for ball in self.balls:
            ball.update(dt, events)
        self.update_current_ball()
        for ball in self.balls[:]:
            if ball.has_sunk():
                self.balls.remove(ball)
        for particle in self.particles:
            particle.update(dt, events)
        for particle in self.particles[:]:
            if particle.dead:
                self.particles.remove(particle)
        for particle in self.floor_particles:
            particle.update(dt, events)
        for particle in self.floor_particles[:]:
            if particle.dead:
                self.floor_particles.remove(particle)
        self.map.update(dt, events)
        self.camera.update(dt, events)
        self.camera.object_to_track = self.current_room()
        if self.no_enemies():
            self.game.combat.set_volume(0)
            self.game.exploring.set_volume(1)

    def draw(self, surface, offset=(0, 0)):
        surface.fill(c.BLACK)
        offset = self.camera.add_offset(offset)
        self.map.draw(surface, offset=offset)
        for particle in self.floor_particles:
            particle.draw(surface, offset=offset)
        for ball in self.balls:
            ball.draw_shadow(surface, offset=offset)
        for ball in self.balls:
            ball.draw(surface, offset=offset)
        self.player.draw_prediction_line(surface, offset=offset)
        for particle in self.particles:
            particle.draw(surface, offset=offset)

    def balls_are_spawning(self):
        for particle in self.particles:
            if isinstance(particle, PreBall):
                return True
        return False

    def shields_are_spawning(self):
        for particle in self.particles:
            if isinstance(particle, ShieldParticle):
                return True
        return False

    def spawn_balls(self):

        self.current_room().waves_remaining -= 1
        floor_num = self.game.current_floor

        difficulty = self.current_room().base_difficulty * (1 - ((self.current_room().waves_remaining)*.15))
        summon_list = []

        summoned_four_ball = False
        summoned_seven_ball = False

        while(difficulty>0):
            if(floor_num == 1):
                try_summon = random.randint(1,4)
            elif (floor_num == 2):
                try_summon = random.randint(1, 6)
            elif floor_num > 2 and floor_num<5:
                try_summon = random.randint(1,7)
            else:
                try_summon = random.randint(3, 14)
                try_summon = try_summon % 7

            if random.random() < ((math.e**( ((floor_num +2)/3)  * -1)) * -1 + .3)* 1.5:
                try_shield = 1
            else:
                try_shield = 0
            if(difficulty - (c.DIFFICULTY_LOOKUP[try_summon - 1] + try_shield*3)>= -1 and not (try_summon == 4 and summoned_four_ball) and not (try_summon == 7 and summoned_seven_ball)):
                difficulty -= c.DIFFICULTY_LOOKUP[try_summon - 1]
                if(try_summon == 4):
                    summoned_four_ball = True
                elif(try_summon == 7):
                    summoned_seven_ball = True
                summon_list.append((try_summon, try_shield))
            else:
                print("FAIL DIFF = " + str(difficulty - c.DIFFICULTY_LOOKUP[try_summon - 1] ) + " attempt on : " + str(try_summon))


        print(len(summon_list))
        summon_list.sort(key=lambda summon: (c.DIFFICULTY_LOOKUP[summon[0] - 1] * (random.random()+.5)* -1) )
        print(len(summon_list))

        offset = self.current_room().center()
        #self.balls += [Ball(self.game, offset[0] - 200, offset[1] - 140)]
        spawn_locations = self.current_room().find_spawn_locations(len(summon_list))
        print("SPAWNING" + str(summon_list))

        if(spawn_locations != False):
            for i in range(0,len(spawn_locations)):
                if(summon_list[i][1] == 0):
                    if(summon_list[i][0] == 1):
                        self.particles += [PreBall(self.game, OneBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                    if (summon_list[i][0] == 2):
                        self.particles += [PreBall(self.game, TwoBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                    if (summon_list[i][0] == 3):
                        self.particles += [PreBall(self.game, ThreeBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                    if (summon_list[i][0] == 4):
                        self.particles += [PreBall(self.game, FourBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                    if (summon_list[i][0] == 5):
                        self.particles += [PreBall(self.game, FiveBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                    if (summon_list[i][0] == 6):
                        self.particles += [PreBall(self.game, SixBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                    if (summon_list[i][0] == 7):
                        self.particles += [PreBall(self.game, SevenBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                else:
                    if (summon_list[i][0] == 1):
                        pre_shell = OneBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]
                    if (summon_list[i][0] == 2):
                        pre_shell = TwoBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]
                    if (summon_list[i][0] == 3):
                        pre_shell = ThreeBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]
                    if (summon_list[i][0] == 4):
                        pre_shell = FourBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]
                    if (summon_list[i][0] == 5):
                        pre_shell = FiveBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]
                    if (summon_list[i][0] == 6):
                        pre_shell = SixBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]
                    if (summon_list[i][0] == 7):
                        pre_shell = SevenBall(self.game, spawn_locations[i][0], spawn_locations[i][1])
                        shelled = Shelled(self.game, pre_shell)
                        self.particles += [PreBall(self.game, shelled)]


        else:
            print("SPAWNING FAILED")

        self.force_player_next = True
        self.game.combat.set_volume(100)
        self.game.exploring.set_volume(0)

    def spawn_balls_first_room(self):

        print("TUTORIAL ROOM")
        self.current_room().waves_remaining -= 1
        floor_num = self.game.current_floor

        difficulty = self.current_room().base_difficulty * (1 - ((self.current_room().waves_remaining)*.15))
        summon_list = []

        if(self.current_room().waves_remaining == 2):
            summon_list.append(1)
            pass
        if(self.current_room().waves_remaining == 1):
            summon_list.append(2)
            summon_list.append(1)
            pass


        offset = self.current_room().center()
        #self.balls += [Ball(self.game, offset[0] - 200, offset[1] - 140)]
        spawn_locations = self.current_room().find_spawn_locations(len(summon_list))
        print("SPAWNING" + str(summon_list))

        if(spawn_locations != False):
            for i in range(0,len(spawn_locations)):
                if(summon_list[i] == 1):
                    self.particles += [PreBall(self.game, OneBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 2):
                    self.particles += [PreBall(self.game, TwoBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 3):
                    self.particles += [PreBall(self.game, ThreeBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 4):
                    self.particles += [PreBall(self.game, FourBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 5):
                    self.particles += [PreBall(self.game, FiveBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 6):
                    self.particles += [PreBall(self.game, SixBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 7):
                    self.particles += [PreBall(self.game, SevenBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]


        else:
            print("SPAWNING FAILED")

        self.force_player_next = True
        self.game.combat.set_volume(100)
        self.game.exploring.set_volume(0)


    def current_room(self):
        return self.map.get_at_pixels(*self.player.pose.get_position())