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
        speed = random.random() * 1200 * intensity
        angle = random.random() * 360
        self.velocity = Pose((speed, 0), 0)
        self.velocity.rotate_position(angle)
        self.radius = 6
        self.color = c.WHITE
        self.duration = 0.3
        self.intensity = intensity

    def update(self, dt, events):
        super().update(dt, events)
        self.pose += self.velocity * dt
        self.velocity *= 0.05**dt

    def draw(self, surface, offset=(0, 0)):
        if self.pose.x + offset[0] < -100 or self.pose.x + offset[0] > c.WINDOW_WIDTH + 100 or self.pose.y + offset[1] < -100 or self.pose.y + offset[1] > c.WINDOW_HEIGHT + 100:
            return
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


class PoofBit(Particle):
    def __init__(self, game, x, y):
        super().__init__(game)
        self.radius = 16 + random.random()*10
        self.duration = self.radius * 0.03
        speed = random.random() * 100 + 80
        angle = random.random() * 360
        self.velocity = Pose((speed, 0), 0)
        self.velocity.rotate_position(angle)
        self.pose = Pose((x, y), 0)
        self.color = None

    def get_alpha(self):
        return 255

    def update(self, dt, events):
        super().update(dt, events)
        self.pose += self.velocity * dt
        self.velocity *= 0.1**dt

    def get_scale(self):
        return 1 - self.through(1.5)

    def get_color(self):
        if self.color:
            return self.color
        else:
            return (int(150 - 50*self.through()),)*3

    def draw(self, surf, offset=(0, 0)):
        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        radius = self.radius * self.get_scale()

        pygame.draw.circle(surf, self.get_color(), (x, y), radius)


class WallAppear(PoofBit):
    def __init__(self, game, x, y):
        super().__init__(game, x, y)
        self.radius = 20 + random.random()*25
        self.duration = self.radius * 0.03
        speed = random.random()*100 + 80
        self.pose = Pose((x, y), 0)
        self.velocity = Pose((speed, 0), 0)
        angle = random.random() * 360
        self.velocity.rotate_position(angle)
        self.pose += self.velocity * 0.1

    def draw(self, surf, offset=(0, 0)):
        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        radius = self.radius * self.get_scale()
        color = (c.BLACK)
        pygame.draw.circle(surf, color, (x, y), radius)

class BubbleBurst(Particle):
    def __init__(self, game, x, y, radius=90):
        super().__init__(game)
        self.pose = Pose((x, y), 0)
        self.radius = radius
        self.duration = 0.25

    def get_scale(self):
        return 1+self.through(1.5)/2

    def get_alpha(self):
        return (1 - self.through(2))

    def color(self):
        each = int(255 - 255*self.through(2))
        return each, each, each

    def draw(self, surface, offset=(0, 0)):
        radius = self.radius * self.get_scale()
        surf = pygame.Surface((int(radius*2), int(radius*2)))
        surf.fill(c.BLACK)
        pygame.draw.circle(surf, self.color(), (int(radius), int(radius)), int(radius))
        surface.blit(surf, (self.pose.x + offset[0] - surf.get_width()//2, self.pose.y + offset[1] - surf.get_height()//2), special_flags=pygame.BLEND_ADD)


class PreBall(Particle):
    def __init__(self, game, ball, grow_time = .3, drop_time = .4):
        super().__init__(game)
        self.ball = ball
        self.pose = self.ball.pose.copy()
        self.grow_time = grow_time
        self.drop_time = drop_time
        self.duration = self.grow_time + self.drop_time

    def destroy(self):
        super().destroy()
        self.game.current_scene.balls.append(self.ball)
        self.ball.poof(on_land=True)

    def get_scale(self):
        if self.age > self.grow_time:
            return 1
        else:
            return (self.age / self.grow_time)**0.7

    def get_alpha(self):
        if self.age < self.grow_time:
            return 255
        else:
            return (1 - (self.age - self.grow_time)/(self.duration - self.grow_time))*255

    def get_height(self):
        max_height = 35
        if self.age < self.grow_time:
            return max_height
        else:
            return (1 - ((self.age - self.grow_time)/(self.duration - self.grow_time))**4) * max_height

    def draw(self, surf, offset=(0, 0)):
        r = self.ball.radius * self.get_scale()
        orb = pygame.Surface((r*2, r*2))
        orb.fill(c.BLACK)
        orb.set_colorkey(c.BLACK)
        pygame.draw.circle(orb, c.WHITE, (r, r), r)
        orb.set_alpha(self.get_alpha())

        x = self.pose.x + offset[0]
        y = self.pose.y + offset[1]
        if self.age > self.grow_time:
            self.ball.draw(surf, (offset[0], offset[1] - self.get_height()))

        surf.blit(orb, (x - orb.get_width()//2, y - orb.get_height()//2 - self.get_height()))

class GravityParticle(Particle):
    def __init__(self, game, ball):
        super().__init__(game)
        self.pose_rel = Pose((0, 0), 0)
        speed = c.GRAVITY_RADIUS*2 * (ball.scale * 2 - .999)
        self.velocity = Pose((speed, 0), 0)
        self.velocity.rotate_position(random.random()*360)
        self.duration = 0.5
        self.radius = 4
        self.ball = ball

    def get_scale(self):
        x = self.through()
        return -(2*x - 1)**2 + 1

    def get_alpha(self):
        return 255

    def get_color(self):
        return (100, 40, 110)

    def update(self, dt, events):
        super().update(dt, events)
        self.pose_rel += self.velocity*dt

    def draw(self, surf, offset=(0, 0)):
        if self.velocity.magnitude() <= 5:
            return
        r = int(self.radius*self.get_scale())
        orb = pygame.Surface((r*3, r*2))
        orb.fill(c.BLACK)
        orb.set_colorkey(c.BLACK)
        pygame.draw.ellipse(orb, self.get_color(), (0, 0, r*3, r*2), r)
        orb = pygame.transform.rotate(orb, -math.atan2(self.velocity.y, self.velocity.x)*180/math.pi)
        surf.blit(orb,
                  (self.ball.pose.x + self.pose_rel.x + offset[0] - orb.get_width()//2, self.ball.pose.y + self.pose_rel.y + offset[1] - orb.get_height()//2),
                  special_flags=pygame.BLEND_ADD)

class ShieldParticle(Particle):
    def __init__(self, game, parent, target, delay=0):
        from ball import Shelled  # Is this good code? No. Does it work? Maybe.

        super().__init__(game)
        self.target = target
        self.target_start_radius = target.radius
        self.start_pose = parent.pose.copy()
        self.shelled_target = Shelled(self.game, target)
        self.target.outline_hidden = False
        self.shloop_time = 0.5
        self.fade_time = 0.5
        self.duration = self.shloop_time + self.fade_time
        self.delay = delay
        self.has_transformed = False

        self.r = int(self.shelled_target.radius)
        self.surf = pygame.Surface((self.r*2, self.r*2))
        self.surf.fill(c.BLACK)
        self.surf.set_colorkey(c.BLACK)
        pygame.draw.circle(self.surf, self.get_color(), (self.r, self.r), self.r)

    def get_scale(self):
        if self.age < self.shloop_time:
            return (self.age / self.shloop_time) **0.3
        else:
            return 1

    def get_target_radius(self):
        # How big the target should be
        return int(self.target_start_radius + (self.shelled_target.radius - self.target_start_radius) * self.through())

    def get_alpha(self):
        if self.age < self.shloop_time:
            return ((self.age/self.shloop_time) * 0.5 + 0.5)**0.2*255
        else:
            return (1 - (self.age - self.fade_time)/(self.duration - self.fade_time)) * 255

    def get_color(self):
        return c.WHITE

    def get_pose(self):
        if self.age > self.shloop_time:
            return self.target.pose.copy()
        diff = self.target.pose - self.start_pose
        through = (self.age/self.shloop_time)**2
        offset = diff * through
        return offset + self.start_pose

    def update(self, dt, events):
        super().update(dt, events)
        if self.delay > 0:
            self.age = 0
            self.delay -= dt
        if self.age > self.shloop_time and not self.has_transformed and not self.target.sunk:
            self.target.gain_shell()
            self.has_transformed = True

    def draw(self, surface, offset=(0, 0)):
        if self.delay > 0:
            return
        pose = self.get_pose()

        r = self.r * self.get_scale()
        surf = pygame.transform.scale(self.surf, (int(r*2), int(r*2)))
        surf.set_alpha(self.get_alpha())
        x = pose.x + offset[0] - r
        y = pose.y + offset[1] - r
        surface.blit(surf, (x, y))

class HeartBubble(Particle):
    def __init__(self, game, parent):
        super().__init__(game)
        self.game = game
        self.radius = 12
        self.duration = 0.75

        speed = parent.radius / self.duration
        self.pose = Pose((0, 0), 0)
        self.velocity = Pose((speed, 0), 0)
        self.velocity.rotate_position(random.random()*360)
        self.parent = parent

    def get_scale(self):
        return (1 - self.through(0.7)) * self.parent.scale

    def get_color(self):
        return (45, 0, 0)

    def update(self, dt, events):
        super().update(dt, events)
        self.pose += self.velocity * dt

    def draw(self, surface, offset=(0, 0)):
        x = self.parent.pose.x + offset[0] + self.pose.x * self.parent.scale
        y = self.parent.pose.y + offset[1] + self.pose.y * self.parent.scale
        r = self.get_scale() * self.radius

        pygame.draw.circle(surface, self.get_color(), (x, y), r)
