import os

FPS = 60

WINDOW_WIDTH = 1600
WINDOW_HEIGHT = 900
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

GAME_TITLE = "Super pool cool game!!!!1!1!"

DEFAULT_BALL_RADIUS = 30
DEFAULT_BALL_CONSTANT_DRAG = 200
DEFAULT_BALL_MULT_DRAG = .08
DEFAULT_BALL_MAX_SPEED = 2500
TABLE_FRICTION_BALL_SPIN_RATIO = .12
MIN_ROTATIONAL_VELOCITY = .5

MIN_WALL_BOUNCE_SPEED = 10
WALL_BOUNCE_FACTOR = .95
MIN_BOUNCE_REDUCTION_SPEED = 50

AI_MAX_ANGLE_REDUCTION = 100 #IN RADIANS SET TP 100 TO DISABLE

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
UP_WALL = "U"
DOWN_WALL = "D"
LEFT_WALL = "L"
RIGHT_WALL = "R"

ROOMS = list(range(16))
#ROOMS = [999]

FULLSCREEN = False

DEBUG = False

UP = 1
RIGHT = 2
DOWN = 3
LEFT = 4

BEFORE_HIT = 0
AFTER_HIT = 1


SIM_FPS = 60
SIM_ITERATIONS = 150
SIM_MAX_DIST = 650

VARIABLE_SIM_SPEED = True
SIM_MOVEMENT=25
SIM_MIN_FPS = 20
SIM_NEAR_WALL_STEP_REDUCTION=1

AI_PREDICTION_ATTEMPTS = 100
AI_MAX_DEFLECTION_ANGLE_ATTEMPTED = 85

AI_SIM_FPS = 30
AI_SIM_ITERATIONS = 100
AI_SIM_MAX_DIST = 5000

AI_VARIABLE_SIM_SPEED = True
AI_SIM_MOVEMENT= 60
AI_SIM_MIN_FPS = 3
AI_SIM_NEAR_WALL_STEP_REDUCTION=1

BPM = 112

def dprint(thing):
    if DEBUG:
        print(thing)

def image_path(rel):
    return os.path.join("images", rel)

def sound_path(rel):
    return os.path.join("sounds", rel)