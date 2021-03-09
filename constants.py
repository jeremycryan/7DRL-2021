import os

FPS = 60

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

GAME_TITLE = "Super pool cool game!!!!1!1!"

DEFAULT_BALL_RADIUS = 30
DEFAULT_BALL_CONSTANT_DRAG = 40
DEFAULT_BALL_MULT_DRAG = .08
DEFAULT_BALL_MAX_SPEED = 2500
MIN_WALL_BOUNCE_SPEED = 10
WALL_BOUNCE_FACTOR = .95
MIN_BOUNCE_REDUCTION_SPEED = 50


BLACK = 0, 0, 0
WHITE = 255, 255, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
BLUE = 0, 0, 255
CYAN = 0, 255, 255
MAGENTA = 255, 0, 255
YELLOW = 255, 255, 0

TILE_SIZE = 64
COLLIDER_SIZE = 10


ROOM_WIDTH_TILES = 20
ROOM_HEIGHT_TILES = 12

EMPTY = "."
WALL = "X"
POCKET = "P"

FULLSCREEN = False

DEBUG = True

UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4

def dprint(thing):
    if DEBUG:
        print(thing)

def image_path(rel):
    return os.path.join("images", rel)