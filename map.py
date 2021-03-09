import random

import pygame

from primitives import GameObject
import constants as c
from pocket import Pocket


class Map(GameObject):
    def __init__(self, game, width=8, height=12):
        self.game = game
        self.width = width
        self.height = height
        self.generate_rooms()

    def generate_rooms(self):
        self.rooms = [[Room(self.game, x, y) for x in range(self.width)] for y in range(self.height)]

    def get_at(self, x, y):
        return self.rooms[int(y)][int(x)]

    def get_at_pixels(self, x, y):
        return self.get_at(x/c.TILE_SIZE/c.ROOM_WIDTH_TILES, y/c.TILE_SIZE/c.ROOM_HEIGHT_TILES)

    def room_iter(self):
        for row in self.rooms:
            for room in row:
                yield room

    def update(self, dt, events):
        for room in self.room_iter():
            room.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        for room in self.room_iter():
            room.draw(surface, offset=offset)

    def tiles_near(self, pose, radius):
        radius *= 1.0
        min_x = int((pose.x - radius)/c.TILE_SIZE)
        min_y = int((pose.y - radius)/c.TILE_SIZE)
        max_x = int((pose.x + radius)/c.TILE_SIZE)
        max_y = int((pose.y + radius)/c.TILE_SIZE)

        for room in self.room_iter():
            px = room.x * c.ROOM_WIDTH_TILES * c.TILE_SIZE
            py = room.y * c.ROOM_HEIGHT_TILES * c.TILE_SIZE
            if px < min_x * c.TILE_SIZE - c.ROOM_WIDTH_TILES * c.TILE_SIZE or px > max_x * c.TILE_SIZE:
                continue
            if py < min_y * c.TILE_SIZE - c.ROOM_WIDTH_TILES * c.TILE_SIZE or py > max_y * c.TILE_SIZE:
                continue
            for tile in room.tile_iter():
                if tile.x < min_x or tile.y < min_y or tile.x > max_x or tile.y > max_y:
                    continue
                yield tile

    def pockets_iter(self):
        for room in self.room_iter():
            for pocket in room.pockets:
                yield pocket


class Room(GameObject):
    def __init__(self, game, x, y):
        self.x = x
        self.y = y
        tile_x_off = self.x * c.ROOM_WIDTH_TILES
        tile_y_off = self.y * c.ROOM_HEIGHT_TILES
        self.tiles = [[Tile(game, random.choice([c.EMPTY, c.EMPTY, c.EMPTY, c.EMPTY, c.WALL]), tile_x_off + x, tile_y_off + y)
                       for x in range(c.ROOM_WIDTH_TILES)]
                      for y in range(c.ROOM_HEIGHT_TILES)]
        self.game = game
        self.openings = []
        path = f"rooms/room_{random.choice([0, 1, 2, 3])}.txt"
        self.pockets = []
        self.populate_from_path(path)

    def add_tile_collisions(self):
        for tile in self.tile_iter():
            x, y = tile.x, tile.y
            x -= self.x * c.ROOM_WIDTH_TILES
            y -= self.y * c.ROOM_HEIGHT_TILES
            if x >= c.ROOM_WIDTH_TILES or y >= c.ROOM_HEIGHT_TILES:
                continue
            if not tile.collidable:
                continue
            tile.left_bumper = True
            tile.right_bumper = True
            tile.down_bumper = True
            tile.up_bumper = True

            if x==0 or self.tiles[y][x-1].collidable:
                tile.left_bumper = False
            if y==0 or self.tiles[y-1][x].collidable:
                tile.up_bumper = False
            if x>=(c.ROOM_WIDTH_TILES-1) or self.tiles[y][x+1].collidable:
                tile.right_bumper = False
            if y>=(c.ROOM_HEIGHT_TILES-1) or self.tiles[y+1][x].collidable:
                tile.down_bumper = False

            if(tile.up_bumper and tile.right_bumper):
                tile.top_right_corner = True
                tile.up_bumper = False
                tile.right_bumper = False;
            elif (tile.up_bumper and tile.left_bumper):
                tile.top_left_corner = True
                tile.up_bumper = False
                tile.left_bumper = False;
            elif (tile.down_bumper and tile.right_bumper):
                tile.bottom_right_corner = True
                tile.down_bumper = False
                tile.right_bumper = False
            elif (tile.down_bumper and tile.left_bumper):
                tile.bottom_left_corner = True
                tile.down_bumper = False
                tile.left_bumper = False


    def populate_from_path(self, path):
        self.pockets = []
        with open(path) as f:
            lines = f.readlines()
        self.openings = [char for char in lines[0].strip()]
        for y, row in enumerate(lines[1:]):
            row = row.strip()
            for x, character in enumerate(row):
                self.tiles[y][x] = Tile(self.game, character, self.x * c.ROOM_WIDTH_TILES + x, self.y * c.ROOM_HEIGHT_TILES + y)
                if character == c.POCKET:
                    self.pockets.append(Pocket(self.game, self.tiles[y][x]))
        self.add_tile_collisions()

    def get_at(self, x, y):
        return self.tiles[int(y)][int(x)]

    def get_at_pixels(self, x, y):
        return self.get_at(x/c.TILE_SIZE, y/c.TILE_SIZE)

    def update(self, dt, events):
        for pocket in self.pockets:
            pocket.update(dt, events)
        for tile in self.tile_iter():
            tile.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        if offset[0] + self.x*c.ROOM_WIDTH_TILES*c.TILE_SIZE < -c.WINDOW_WIDTH - c.TILE_SIZE or \
            offset[1] + self.y*c.ROOM_HEIGHT_TILES*c.TILE_SIZE < -c.WINDOW_HEIGHT - c.TILE_SIZE or \
            offset[0] + self.x*c.ROOM_WIDTH_TILES*c.TILE_SIZE > c.WINDOW_WIDTH or \
            offset[1] + self.y*c.ROOM_HEIGHT_TILES*c.TILE_SIZE > c.WINDOW_HEIGHT:
            return
        for tile in self.tile_iter():
            tile.draw(surface, offset=offset)
        for pocket in self.pockets:
            if pocket.pose.x + offset[0] < -pocket.radius or pocket.pose.x + offset[0] > c.WINDOW_WIDTH + pocket.radius or \
                pocket.pose.y + offset[1] < -pocket.radius or pocket.pose.y + offset[1] > c.WINDOW_HEIGHT + pocket.radius:
                    continue
            pocket.draw(surface, offset=offset)

    def tile_iter(self):
        for row in self.tiles:
            for tile in row:
                yield tile


class Tile(GameObject):
    def __init__(self, game, key, x, y,
                 top_right_corner = False,
                 top_left_corner = False,
                 bottom_right_corner = False,
                 bottom_left_corner = False,
                 down_bumper = False,
                 up_bumper = False,
                 left_bumper = False,
                 right_bumper = False,
                 bounce_factor = .95):
        self.game = game

        self.key = key
        self.collidable = True
        self.surface = pygame.Surface((c.TILE_SIZE, c.TILE_SIZE))
        self.top_right_corner = top_right_corner
        self.top_left_corner = top_left_corner
        self.bottom_right_corner = bottom_right_corner
        self.bottom_left_corner = bottom_left_corner
        self.down_bumper = down_bumper
        self.up_bumper = up_bumper
        self.left_bumper = left_bumper
        self.right_bumper = right_bumper
        self.bounce_factor = bounce_factor

        if key in [c.EMPTY, c.POCKET]:
            self.collidable = False
            if key == c.EMPTY or key==c.POCKET:
                self.surface.fill((30, 80, 30))
            elif key == c.POCKET:
                self.surface.fill(c.MAGENTA)
        else:
            self.surface.fill(c.BLACK)

        self.x = x
        self.y = y

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        x = self.x * c.TILE_SIZE + offset[0]
        y = self.y * c.TILE_SIZE + offset[1]
        if x < -c.TILE_SIZE or x > c.WINDOW_WIDTH or y < -c.TILE_SIZE or y > c.WINDOW_HEIGHT:
            return
        surface.blit(self.surface, (x, y))

        if c.DEBUG:
            bit = pygame.Surface((10, 10))
            bit.fill((100, 150, 100))
            if self.up_bumper:
                surface.blit(bit, (x+c.TILE_SIZE//2 - 5, y))
            if self.down_bumper:
                surface.blit(bit, (x + c.TILE_SIZE//2 - 5, y + c.TILE_SIZE-10))
            if self.right_bumper:
                surface.blit(bit, (x + c.TILE_SIZE - 10, y + c.TILE_SIZE//2 - 5))
            if self.left_bumper:
                surface.blit(bit, (x, y + c.TILE_SIZE//2 - 5))
            if self.bottom_left_corner:
                surface.blit(bit, (x, y + c.TILE_SIZE - 10))
            if self.top_left_corner:
                surface.blit(bit, (x, y))
            if self.top_right_corner:
                surface.blit(bit, (x + c.TILE_SIZE - 10, y))
            if self.bottom_right_corner:
                surface.blit(bit, (x + c.TILE_SIZE - 10, y + c.TILE_SIZE - 10))