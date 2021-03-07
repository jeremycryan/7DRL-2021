import random

import pygame

from primitives import GameObject
import constants as c


class Map(GameObject):
    def __init__(self, game, width=10, height=6):
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

    def get_at(self, x, y):
        return self.tiles[int(y)][int(x)]

    def get_at_pixels(self, x, y):
        return self.get_at(x/c.TILE_SIZE, y/c.TILE_SIZE)

    def update(self, dt, events):
        for tile in self.tile_iter():
            tile.update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        camera = self.game.current_scene.camera
        if offset[0] + self.x*c.ROOM_WIDTH_TILES*c.TILE_SIZE < -c.WINDOW_WIDTH - c.TILE_SIZE or \
            offset[1] + self.y*c.ROOM_HEIGHT_TILES*c.TILE_SIZE < -c.WINDOW_HEIGHT - c.TILE_SIZE or \
            offset[0] + self.x*c.ROOM_WIDTH_TILES*c.TILE_SIZE > c.WINDOW_WIDTH or \
            offset[1] + self.y*c.ROOM_HEIGHT_TILES*c.TILE_SIZE > c.WINDOW_HEIGHT:
            return
        for tile in self.tile_iter():
            tile.draw(surface, offset=offset)

    def tile_iter(self):
        for row in self.tiles:
            for tile in row:
                yield tile


class Tile(GameObject):
    def __init__(self, game, key, x, y):
        self.game = game

        self.key = key
        self.collidable = True
        self.surface = pygame.Surface((c.TILE_SIZE, c.TILE_SIZE))
        if key in [c.EMPTY]:
            self.collidable = False
            self.surface.fill((30, 80, 30))
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