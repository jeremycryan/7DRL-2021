from scene import Scene
import pygame
import constants as c
from button import Button
from level_scene import LevelScene

class MainMenuScene(Scene):

    def __init__(self, game):
        super().__init__(game)
        self.background = pygame.image.load(c.image_path("splash.png"))
        self.background = pygame.transform.scale(self.background, c.WINDOW_SIZE)
        button_surf = pygame.image.load(c.image_path("start_button.png"))
        self.button = Button(button_surf, (400, 100), "play gaem", self.on_button_click)
        self.is_over = False

    def next_scene(self):
        return LevelScene(self.game)

    def on_button_click(self):
        self.is_over = True

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.background, (0, 0))
        self.button.draw(surface, *offset)

    def update(self, dt, events):
        self.button.update(dt, events)