import pygame

from ball import Ball
from primitives import Pose


class Player(Ball):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, 20)
        self.color = (255, 255, 0)

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
        self.velocity = hit_vector.copy()
        print(self.velocity)
