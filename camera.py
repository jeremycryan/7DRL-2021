from primitives import GameObject, Pose
import constants as c
import math
import pygame


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
        mouse_pose = Pose(pygame.mouse.get_pos(), 0) - Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2), 0)
        if not (hasattr(self.game.current_scene, "player") and self.game.current_scene.player.turn_in_progress and self.game.current_scene.player.turn_phase == c.BEFORE_HIT):
            mouse_pose *= 0
        diff = self.object_to_track.pose - self.pose + mouse_pose * 0.12 - self.mid_pose
        if diff.magnitude() > 2:
            self.pose += diff * dt * 5
        self.shake_amp *= 0.005**dt
        if self.shake_amp < 1:
            self.shake_amp = 0
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