import math

import pygame

from ball import Ball
from primitives import Pose
from cue import Cue, BasicCue
import constants as c


class Player(Ball):
    def __init__(self, game, x=0, y=0):
        super().__init__(game, x, y)
        self.color = (255, 255, 0)
        self.active_cue = BasicCue()

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
