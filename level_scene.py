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
        self.loading_new_level = pygame.image.load(c.image_path("loading_new_level.png"))
        self.game.screen.blit(self.loading_new_level, (c.WINDOW_WIDTH//2 - self.loading_new_level.get_width()//2, c.WINDOW_HEIGHT - self.loading_new_level.get_height()))
        pygame.display.flip()
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

        self.black = pygame.Surface(c.WINDOW_SIZE)
        self.black.fill(c.BLACK)
        self.black_alpha = 255
        self.black.set_alpha(self.black_alpha)
        self.black_target_alpha = 0

        self.place_circle = pygame.Surface((c.DEFAULT_BALL_RADIUS*2, c.DEFAULT_BALL_RADIUS*2))
        self.place_circle.fill(c.BLACK)
        pygame.draw.circle(self.place_circle, c.WHITE, (c.DEFAULT_BALL_RADIUS, c.DEFAULT_BALL_RADIUS), c.DEFAULT_BALL_RADIUS)
        self.place_circle.set_alpha(100)
        self.place_circle.set_colorkey(c.BLACK)

        self.bad_place_circle = pygame.Surface((c.DEFAULT_BALL_RADIUS*2, c.DEFAULT_BALL_RADIUS*2))
        self.bad_place_circle.fill(c.BLACK)
        pygame.draw.circle(self.bad_place_circle, c.RED, (c.DEFAULT_BALL_RADIUS, c.DEFAULT_BALL_RADIUS), c.DEFAULT_BALL_RADIUS)
        self.bad_place_circle.set_alpha(100)
        self.bad_place_circle.set_colorkey(c.BLACK)

        self.scratch_text = pygame.image.load(c.image_path("scratch_text.png"))
        self.scratch_text_back = pygame.image.load(c.image_path("scratch_text_back.png"))

        if not self.game.music_started:
            self.game.exploring.play(-1)
            self.game.combat.play(-1)
            self.music_started = time.time()
        else:
            self.music_started = self.game.music_started
        self.game.combat.set_volume(0)
        self.game.exploring.set_volume(0.18)
        self.moves_used = 0
        self.boss_is_dead = False
        self.player_advancing = False
        self.has_lost = False
        self.last_poses = []
        self.now_poses = []
        self.last_turn_started = time.time()

        self.life_icon = pygame.image.load(c.image_path("life_icon.png"))
        self.empty_life_icon = pygame.image.load(c.image_path("life_icon_empty.png"))

    def shake(self, amt, pose=None):
        if not self.game.in_simulation:
            self.camera.shake(amt, pose)

    def player_just_sunk(self):
        self.current_room().player_died_here = True
        if self.player_advancing:
            self.start_fadeout()

    def start_fadeout(self):
        self.black_target_alpha = 255

    def update_current_ball(self):
        if self.player_advancing or self.player.sunk:
            return
        if self.balls_are_spawning() or self.shields_are_spawning():
            return
        if not self.current_ball.turn_in_progress or self.current_ball.sunk:
            self.last_turn_started = time.time()
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

    def is_valid_drop_location(self, x, y):
        if self.player_advancing:
            return False
        # Check if player drop location is a-ok
        pose = Pose((x, y), 0)
        x0, y0 = self.camera.add_offset((0, 0))
        pixel_pose = Pose((x - x0 + c.DEFAULT_BALL_RADIUS, y - y0 + c.DEFAULT_BALL_RADIUS), 0)
        for tile in self.map.tiles_near(pixel_pose, c.DEFAULT_BALL_RADIUS):
            if tile.collidable:
                return False
        for ball in self.balls:
            if ball.is_player:
                continue
            if (ball.pose - pixel_pose).magnitude() < c.DEFAULT_BALL_RADIUS + ball.radius:
                return False
        if self.map.get_at_pixels(*pixel_pose.get_position()) is not self.current_room():
           return False
        return True

    def no_enemies(self):
        if self.balls_are_spawning():
            return False
        for ball in self.balls:
            if ball is not self.player:
                return False
        return True

    def total_velocity(self):
        return sum([ball.velocity.magnitude() for ball in self.balls])

    def all_balls_below_speed(self, speed=5):
        # if time.time() - self.last_turn_started > 10:
        #     self.last_turn_started = time.time()
        #     self.current_ball.turn_in_progress = False
        #     return True
        for ball in self.balls:
            if ball.velocity.magnitude() > speed:
                poses = [ball.pose.copy() for ball in self.balls]
                if len(poses) != len(self.last_poses) or len(poses) == 1:
                    return False
                else:
                    total_change = sum([(ball_pose - pose).magnitude() for ball_pose, pose in zip(poses, self.last_poses)])
                    if total_change < 0.000001 and not self.game.in_simulation and not any([ball.is_simulating for ball in self.balls]) and time.time() - self.last_turn_started > 10:
                        self.last_turn_started = time.time()
                        self.current_ball.turn_in_progress = False
                        self.current_ball.turn_phase = c.AFTER_HIT
                        return True
                    else:
                        return False
        return True

    def check_click(self, events):
        if not self.player.sunk or self.has_lost:
            return

        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.player.sunk = False
                    self.player.tractor_beam_target = None
                    self.player.velocity = Pose((0, 0), 0)
                    self.player.scale = 1
                    self.player.alpha = 255
                    self.player.target_scale = 1
                    self.player.target_alpha = 255
                    self.player.can_collide = True
                    self.player.has_poofed = False
                    mpos = pygame.mouse.get_pos()
                    x = -(self.camera.add_offset((0, 0))[0]) + mpos[0]
                    y = -(self.camera.add_offset((0, 0))[1]) + mpos[1]
                    self.player.pose.x = x
                    self.player.pose.y = y
                    self.particles.append(PreBall(self.game, self.player))

    def update(self, dt, events):

        if self.current_room().is_boss_room and self.no_enemies() and self.current_room().enemies_have_spawned:
            self.boss_is_dead = True

        self.check_click(events)
        self.has_lost = self.game.player_lives < 0
        if self.has_lost:
            self.black_target_alpha = 255

        for ball in self.balls:
            ball._did_collide = False;
        for ball in self.balls:
            ball.update(dt, events)
        self.update_current_ball()
        self.last_poses = self.now_poses
        self.now_poses = [ball.pose.copy() for ball in self.balls]
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
            self.game.exploring.set_volume(0.18)

        if self.player.sunk:
            self.force_player_next = True
            self.player.scale = 1

        if self.black_alpha > self.black_target_alpha:
            self.black_alpha = max(self.black_target_alpha, self.black_alpha - 800*dt)
        else:
            self.black_alpha = min(self.black_target_alpha, self.black_alpha + 800*dt)

        if self.black_alpha == 255 and (self.player_advancing or self.has_lost):
            self.is_over = True

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

        self.draw_lives(surface, offset=offset)

        self.draw_drop_preview(surface)

        if self.black_alpha > 0:
            self.black.set_alpha(self.black_alpha)
            surface.blit(self.black, (0, 0))

    def draw_drop_preview(self, surface, offset=(0, 0)):
        if not self.player.sunk or self.player_advancing or self.has_lost:
            return

        surface.blit(self.scratch_text_back, (c.WINDOW_WIDTH//2 - self.scratch_text_back.get_width()//2, c.WINDOW_HEIGHT//2 - self.scratch_text_back.get_height()//2), special_flags=pygame.BLEND_MULT)
        surface.blit(self.scratch_text, (c.WINDOW_WIDTH//2 - self.scratch_text.get_width()//2, c.WINDOW_HEIGHT//2 - self.scratch_text.get_height()//2), special_flags=pygame.BLEND_ADD)

        mpos = pygame.mouse.get_pos()
        x = mpos[0] + offset[0] - self.place_circle.get_width()//2
        y = mpos[1] + offset[1] - self.place_circle.get_height()//2
        if self.is_valid_drop_location(x, y):
            surface.blit(self.place_circle, (x, y))
        else:
            surface.blit(self.bad_place_circle, (x, y))

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
                if(try_summon == 1 and random.random()>.5):
                    try_summon = random.randint(2, 6)
            elif floor_num > 2 and floor_num<5:
                try_summon = random.randint(1,7)
                if (try_summon == 1 and random.random() > .5):
                    try_summon = random.randint(2, 7)
            else:
                try_summon = random.randint(3, 14)
                try_summon = try_summon % 7
                if (try_summon == 1 and random.random() > .5):
                    try_summon = random.randint(2, 7)

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


        #print(len(summon_list))
        summon_list.sort(key=lambda summon: (c.DIFFICULTY_LOOKUP[summon[0] - 1] * (random.random()+1.3)* -1))
        summon_list = summon_list[:floor_num+1]
        #print(len(summon_list))

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
        self.game.combat.set_volume(0.3)
        self.game.exploring.set_volume(0.8)

    def spawn_balls_first_room(self):

        print("TUTORIAL ROOM")
        self.current_room().waves_remaining -= 1

        summon_list = []

        if(self.current_room().waves_remaining == 1):
            summon_list.append(2)
            summon_list.append(1)
            pass
        else:
            summon_list.append(1)
            pass


        offset = self.current_room().center()
        #self.balls += [Ball(self.game, offset[0] - 200, offset[1] - 140)]
        spawn_locations = self.current_room().find_spawn_locations(len(summon_list))

        if(spawn_locations != False):
            for i in range(0,len(spawn_locations)):
                print(i)
                if(summon_list[i] == 1):
                    self.particles += [PreBall(self.game, OneBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]
                if (summon_list[i] == 2):
                    self.particles += [PreBall(self.game, TwoBall(self.game, spawn_locations[i][0], spawn_locations[i][1]))]




        else:
            print("SPAWNING FAILED")

        self.force_player_next = True
        self.game.combat.set_volume(0.3)
        self.game.exploring.set_volume(0.8)

    def spawn_boss(self):

        if self.boss_is_dead:
            return
        self.current_room().waves_remaining -= 1
        floor_num = self.game.current_floor


        offset = self.current_room().center()
        spawn_locations = self.current_room().find_spawn_locations(1)

        if(spawn_locations != False):
            self.particles += [PreBall(self.game, BossBall(self.game, spawn_locations[0][0], spawn_locations[0][1]))]
        else:
            print("SPAWNING FAILED")

        self.force_player_next = False
        self.game.combat.set_volume(0.3)
        self.game.exploring.set_volume(0.8)



    def current_room(self):
        return self.map.get_at_pixels(*self.player.pose.get_position())

    def draw_lives(self, screen, offset=(0, 0)):
        life_spacing = 20
        x = int(c.WINDOW_WIDTH/2 - self.life_icon.get_width()/2 - life_spacing * (self.game.player_max_lives - 1) / 2)
        y = 20
        for i in list(range(self.game.player_max_lives))[::-1]:
            surface = self.life_icon
            if i >= self.game.player_lives:
                surface = self.empty_life_icon
            screen.blit(surface, (x + i*life_spacing, y))


    def next_scene(self):
        if self.player_advancing:
            self.game.current_floor += 1
            self.game.player_lives += 1
            if self.game.player_lives > self.game.player_max_lives:
                self.game.player_lives = self.game.player_max_lives
            self.game.music_started = self.music_started
            return LevelScene(self.game)
        else:
            # player has lost
            from main_menu_scene import MainMenuScene
            self.game.exploring.fadeout(400)
            self.game.combat.fadeout(400)
            return MainMenuScene(self.game)