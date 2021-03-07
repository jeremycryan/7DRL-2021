import math

import pygame

from ball import Ball
from primitives import Pose
from cue import Cue, BasicCue


class Player(Ball):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, 20)
        self.color = (255, 255, 0)
        self.active_cue = BasicCue()

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pose = Pose(pygame.mouse.get_pos(), 0)
                    my_pose = self.pose.copy()  # TODO once camera movement exists, account for it
                    self.cue_hit(mouse_pose - my_pose)

        super().update(dt, events)

    def cue_hit(self, hit_vector):
        # TODO use self.knock, and account for cue type
        # self.velocity = hit_vector.copy()
        angle = math.atan2(-hit_vector.y, hit_vector.x) * 180/math.pi
        power = hit_vector.magnitude()/5
        if power > 100:
            power = 100
        self.velocity *= 0
        self.knock(self.active_cue, angle, power)
