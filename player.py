import math

import pygame

from ball import Ball
from primitives import Pose
from cue import Cue, BasicCue
import constants as c

from copy import copy


class Player(Ball):
    def __init__(self, game, x=0, y=0):
        super().__init__(game, x, y)
        self.color = (255, 255, 0)
        self.active_cue = BasicCue()
        self.is_player = True
        self.has_collided = False
        self.collided_with = None

    def load_back_surface(self):
        self.back_surface = pygame.image.load(c.image_path("player_back.png"))

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pose = Pose(pygame.mouse.get_pos(), 0) + self.game.current_scene.camera.pose
                    my_pose = self.pose.copy()  # TODO once camera movement exists, account for it
                    self.cue_hit(mouse_pose - my_pose)

        super().update(dt, events)

        current_room = self.game.current_scene.current_room()
        if self.is_completely_in_room() and not current_room.enemies_have_spawned:
            current_room.doors_close()
            current_room.spawn_enemies()
        elif current_room.enemies_have_spawned and not current_room.doors_are_open and self.game.current_scene.no_enemies():
            current_room.doors_open()

    def take_turn(self):
        pass

    def cue_hit(self, hit_vector):
        # TODO use self.knock, and account for cue type
        # self.velocity = hit_vector.copy()

        if self.turn_phase != c.BEFORE_HIT or not self.turn_in_progress:
            return
        elif self.turn_in_progress:
            self.turn_phase = c.AFTER_HIT

        angle = math.atan2(-hit_vector.y, hit_vector.x) * 180/math.pi
        power = hit_vector.magnitude()/5
        if power > 100:
            power = 100
        self.velocity *= 0
        self.knock(self.active_cue, angle, power)

    def draw_prediction_line(self, screen, offset=(0, 0)):
        self.game.in_simulation = True
        player_copy = copy(self)
        player_copy.pose = self.pose.copy()
        player_copy.velocity = self.velocity.copy()
        player_copy.collide_with_other_ball_2 = player_copy.mock_collision
        mouse_pose = Pose(pygame.mouse.get_pos(), 0) + self.game.current_scene.camera.pose
        my_pose = self.pose.copy()
        player_copy.cue_hit(mouse_pose - my_pose)

        traveled = 0
        positions = []
        for i in range(c.SIM_ITERATIONS):

            if(c.VARIABLE_SIM_SPEED):
                if player_copy.velocity.magnitude() > 3:
                   sim_update = (c.SIM_MOVEMENT/player_copy.velocity.magnitude())
                else:
                    sim_update = 1 / c.SIM_MIN_FPS
                #mapTiles = self.game.current_scene.map.tiles_near(self.pose, self.radius + );
            else:
                sim_update = 1 / c.SIM_FPS

            player_copy.update(sim_update, [])
            positions.append(player_copy.pose.copy())
            if player_copy.has_collided:
                break

        surf = pygame.Surface((self.radius*2, self.radius*2))
        surf.fill(c.BLACK)
        pygame.draw.circle(surf, c.WHITE, (self.radius, self.radius), 2)
        alpha = 255
        surf.set_colorkey(c.BLACK)
        for pose in positions[::1]:
            alpha -= 250/c.SIM_ITERATIONS
            surf.set_alpha(alpha)
            screen.blit(surf, (pose.x + offset[0] - self.radius, pose.y + offset[1] - self.radius))

        self.game.in_simulation = False

    def draw(self, screen, offset=(0, 0)):
        if self.turn_in_progress and self.turn_phase == c.BEFORE_HIT:
            self.draw_prediction_line(screen, offset=offset)
        super().draw(screen, offset=offset)

    def mock_collision(self, other):
        if self.has_collided or other.is_player:
            return
        self.has_collided = True
        self.collided_with = other
