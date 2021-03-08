##!/usr/bin/env python3

import pygame
import math

from primitives import GameObject, Pose
import random

import constants as c


class Particle(GameObject):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.age = 0
        self.duration = None
        self.dead = False

    def get_alpha(self):
        return 255

    def get_scale(self):
        return 1

    def through(self, loading=1):
        """ Increase loading argument to 'frontload' the animation. """
        if self.duration is None:
            return 0
        else:
            return 1 - (1 - self.age / self.duration)**loading

    def update(self, dt, events):
        self.age += dt
        if self.duration and self.age > self.duration:
            self.destroy()

    def destroy(self):
        self.dead = True


class Spark(Particle):
    def __init__(self, game, x, y, intensity=1):
        super().__init__(game)
        self.game = game
        self.pose = Pose((x, y), 0)
        speed = random.random() * 1000 * intensity
        angle = random.random() * 360
        self.velocity = Pose((speed, 0), 0)
        self.velocity.rotate_position(angle)
        self.radius = 5
        self.color = c.WHITE
        self.duration = 0.2
        self.intensity = intensity

    def update(self, dt, events):
        super().update(dt, events)
        self.pose += self.velocity * dt
        self.velocity *= 0.05**dt

    def draw(self, surface, offset=(0, 0)):
        stretch = self.velocity.magnitude()/50 + 1
        surf = pygame.Surface((int(self.radius * stretch * self.get_scale()), self.radius * self.get_scale()))
        surf.fill(c.BLACK)
        surf.set_colorkey(c.BLACK)
        pygame.draw.ellipse(surf, self.color, surf.get_rect())
        angle = math.atan2(-self.velocity.y, self.velocity.x)*180/math.pi
        surf = pygame.transform.rotate(surf, angle)
        x = self.pose.x - surf.get_width()//2 + offset[0]
        y = self.pose.y - surf.get_height()//2 + offset[1]
        surf.set_alpha(self.get_alpha())
        surface.blit(surf, (x, y))

    def get_alpha(self):
        return (1 - self.through()) * 255 * self.intensity

    def get_scale(self):
        return (1 - self.through()) * self.intensity


class SmokeBit(Particle):
    def __init__(self, game, x, y):
        super().__init__(game)
        self.radius = 15 + random.random()*15
        self.duration = self.radius * 0.05
        speed = random.random() * 60
        angle = random.random() * 360
        self.velocity = Pose((speed, 0), 0)
        self.velocity.rotate_position(angle)
        self.pose = Pose((x, y), 0)

    def get_alpha(self):
        return 255

    def update(self, dt, events):
        super().update(dt, events)
        self.pose += self.velocity * dt
        self.velocity *= 0.3**dt

    def get_scale(self):
        return 1 - self.through(2)

    def draw(self, surf, offset=(0, 0)):
        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        radius = self.radius * self.get_scale()
        pygame.draw.circle(surf, (200, 200, 200), (x, y), radius)