from primitives import GameObject, Pose
import constants as c
import math


class Camera(GameObject):
    def __init__(self, game, object_to_track):
        self.game = game
        self.object_to_track = object_to_track  # should have a 'pose' attribute with a .x and .y
        self.mid_pose = Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2), 0)
        self.pose = object_to_track.pose - self.mid_pose
        self.shake_amp = 0
        self.since_shake = 0
        self.shake_speed = 30
        self.direction = Pose((1, 1), 0)

    def update(self, dt, events):
        diff = self.object_to_track.pose - self.pose - self.mid_pose
        self.pose += diff * dt * 5
        self.shake_amp *= 0.005**dt
        self.since_shake += dt

    def shake(self, amt, pose=None):
        if amt < self.shake_amp:
            return
        self.shake_amp = amt
        self.since_shake = 0
        if pose:
            self.direction = pose.copy()
        else:
            self.direction = Pose((1, 1), 0)
        self.direction.scale_to(1)

    def draw(self, surf, offset=(0, 0)):
        pass

    def add_offset(self, offset):
        sx = self.direction.x * self.shake_amp * math.cos(self.since_shake*self.shake_speed)
        sy = self.direction.y * self.shake_amp * math.cos(self.since_shake*self.shake_speed)
        return offset[0] - self.pose.x + sx, offset[1] - self.pose.y + sy