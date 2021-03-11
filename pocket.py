from primitives import Pose, GameObject

import constants as c
import pygame


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
        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.surf.fill(c.MAGENTA)
        self.surf.set_colorkey(c.MAGENTA)
        self.eaten = []
        self.hungry = True
        pygame.draw.circle(self.surf, c.CYAN, (self.radius, self.radius), self.radius)

    def update(self, dt, events):
        ds = self.target_scale - self.scale
        self.scale += ds * dt * 5
        if ds * (self.target_scale - self.scale) < 0:
            self.scale = self.target_scale  # Weird way of coding "don't let it oscillate"

    def draw(self, surf, offset=(0, 0)):
        x = self.pose.x - self.surf.get_width()//2 * self.scale + offset[0]
        y = self.pose.y - self.surf.get_height()//2 * self.scale + offset[1]
        surf_to_blit = pygame.transform.scale(self.surf,
            (int(self.surf.get_width()*self.scale),
             int(self.surf.get_height()*self.scale)))
        surf.blit(surf_to_blit, (x, y))

    def swallow(self, ball):
        self.eaten.append(ball)
        ball.sink(self.pose.copy())
        print("NOMNOMNOM")

    def can_swallow(self, ball):
        diff = self.pose - ball.pose
        if abs(diff.x - self.pose.y) < self.radius or abs(diff.y - self.pose.y) < self.radius:
            return False
        if diff.magnitude() < self.radius:
            return True
        return False