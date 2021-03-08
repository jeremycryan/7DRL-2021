import random

import pygame

from primitives import GameObject
import constants as c


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
        radius *= 1.25
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
        self.populate_from_path(path)

    def populate_from_path(self, path):
        with open(path) as f:
            lines = f.readlines()
        self.openings = [char for char in lines[0].strip()]
        for y, row in enumerate(lines[1:]):
            row = row.strip()
            for x, character in enumerate(row):
                self.tiles[y][x] = Tile(self.game, character, self.x * c.ROOM_WIDTH_TILES + x, self.y * c.ROOM_HEIGHT_TILES + y)

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
    def __init__(self, game, key, x, y, top_right_corner = False, top_left_corner = False, bottom_right_corner = False, bottom_left_corner = False, down_bumper = False, up_bumper = False, left_bumper = False, right_bumper = False, bounce_factor = .9):
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
            if key == c.EMPTY:
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