from primitives import Pose, GameObject

import constants as c
import pygame
import time


class Pocket(GameObject):
    def __init__(self, game, tile):
        self.pose = Pose((0, 0), 0)
        self.pose.x = (tile.x + 0.5)*c.TILE_SIZE
        self.pose.y = (tile.y + 0.5)*c.TILE_SIZE
        super().__init__(game)
        self.tile = tile
        self.scale = 1.0
        self.target_scale = 1.0
        self.radius = c.TILE_SIZE * 2**0.5 / 2
        self.surf = pygame.image.load(c.image_path(f"hole{self.ext()}.png"))
        self.surf.set_colorkey(c.WHITE)
        self.surf = pygame.transform.scale(self.surf, (100, 100))
        self.eaten = []
        self.hungry = False
        self.next_floor = False

    def ext(self):
        if self.game.current_floor <= 2:
            return c.POOL
        else:
            return c.HELL

    def update(self, dt, events):
        if self.hungry and self.scale < 1:
            self.scale += dt * 2
            if self.scale > 1:
                self.scale = 1
        elif not self.hungry and self.scale > 0:
            self.scale -= dt * 2
            if self.scale < 0:
                self.scale = 0
        ds = self.target_scale - self.scale
        self.scale += ds * dt * 5
        if ds * (self.target_scale - self.scale) < 0:
            self.scale = self.target_scale  # Weird way of coding "don't let it oscillate"

    def draw(self, surf, offset=(0, 0)):
        if not self.hungry:
            return
        x = self.pose.x - self.surf.get_width()//2 * self.scale + offset[0]
        y = self.pose.y - self.surf.get_height()//2 * self.scale + offset[1]
        surf_to_blit = pygame.transform.scale(self.surf,
            (int(self.surf.get_width()*self.scale),
             int(self.surf.get_height()*self.scale)))
        surf.blit(surf_to_blit, (x, y))

    def swallow(self, ball):
        if not self.game.in_simulation:
            self.eaten.append(ball)
            ball.sink(self.pose.copy())
        elif ball.is_player:
            ball.sink(self.pose.copy())

    def gulp_animation(self):
        self.scale = 1.25

    def open(self):
        self.hungry = True

    def close(self):
        self.hungry = False

    def can_swallow(self, ball):
        if not self.hungry:
            return False
        diff = self.pose - ball.pose
        if abs(diff.x - self.pose.y) < self.radius or abs(diff.y - self.pose.y) < self.radius:
            return False
        if diff.magnitude() < self.radius and not ball.is_player:
            return True
        elif diff.magnitude() + c.PLAYER_POCKET_MARGIN < self.radius:
            return True
        return False


class NextFloorPocket(Pocket):
    def __init__(self, game, room):
        super().__init__(game, room.get_at(0, 0))
        self.radius = 100
        self.surf = pygame.image.load(c.image_path(f"big_hole.png"))
        self.spin = pygame.image.load(c.image_path(f"big_hole_swirl.png"))
        self.spin.set_colorkey(c.MAGENTA)
        self.surf.set_colorkey(c.WHITE)
        self.surf = pygame.transform.scale(self.surf, (200, 200))
        self.room = room
        self.pose = Pose(self.room.center(), 0)
        self.scale = 0
        self.next_floor = True
        self.age = 0

    def can_swallow(self, ball):
        # Only player can go to next floor
        if not ball.is_player:
            return False
        diff = ball.pose - self.pose
        if diff.magnitude() < self.radius*self.scale:
            return True

    def open(self):
        print("OPEN UP")
        super().open()

    def update(self, dt, events):
        if self.hungry:
            if self.scale < 1:
                self.scale += dt
                self.scale = min(1, self.scale)
        self.age += dt

    def swallow(self, ball):
        if ball is self.game.current_scene.player and not self.game.in_simulation:
            self.game.current_scene.player_advancing = True
        super().swallow(ball)

    def draw(self, surf, offset=(0, 0)):
        if not self.hungry:
            return
        if self.scale == 0:
            return
        x, y = self.room.center()
        x = x - self.surf.get_width()//2 * self.scale + offset[0]
        y = y - self.surf.get_height()//2 * self.scale + offset[1]
        surf_to_blit = pygame.transform.scale(self.surf,
            (int(self.surf.get_width()*self.scale),
             int(self.surf.get_height()*self.scale)))
        surf.blit(surf_to_blit, (x, y))

        x, y = self.room.center()
        swirl = pygame.transform.scale(self.spin, (int(self.spin.get_width() * self.scale), int(self.spin.get_height()*self.scale)))
        swirl = pygame.transform.rotate(swirl, self.age*-25)
        x = x - swirl.get_width()//2 + offset[0]
        y = y - swirl.get_height()//2 + offset[1]
        surf.blit(swirl, (x, y))
