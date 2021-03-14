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
        self.button = Button(button_surf, (c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT - 100), "play gaem", self.on_button_click)
        self.is_over = False
        self.shade = pygame.Surface(c.WINDOW_SIZE)
        self.shade.fill(c.BLACK)
        self.shade.set_alpha(0)
        self.shade_alpha = 0
        self.target_alpha = 0

        self.game.player_lives = 3
        self.game.player_max_lives = 3
        self.game.music_started = None
        self.game.current_floor = 1

    def next_scene(self):
        return LevelScene(self.game)

    def on_button_click(self):
        self.target_alpha = 255

    def draw(self, surface, offset=(0, 0)):
        surface.blit(self.background, (0, 0))
        self.button.draw(surface, *offset)
        self.shade.set_alpha(self.shade_alpha)
        surface.blit(self.shade, (0, 0))

    def update(self, dt, events):
        self.button.update(dt, events)
        if self.target_alpha > self.shade_alpha:
            self.shade_alpha += dt * 800
            if self.shade_alpha > self.target_alpha:
                self.shade_alpha = self.target_alpha
                self.is_over = True