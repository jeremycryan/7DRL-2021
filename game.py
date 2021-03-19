import sys

import pygame
import random

import constants as c
from level_scene import LevelScene
from main_menu_scene import MainMenuScene


class Game:
    def __init__(self):
        pygame.init()

        if not c.FULLSCREEN:
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        else:
            self.screen = pygame.display.set_mode(c.WINDOW_SIZE, pygame.FULLSCREEN)

        pygame.display.set_caption(c.GAME_TITLE)
        self.clock = pygame.time.Clock()

        self.in_simulation = False
        self.player_lives = 3
        self.player_max_lives = 3
        self.music_started = None

        self.image_dict = {}

        self.load_sounds()
        self.current_scene = None
        self.current_scene = MainMenuScene(self)
        self.current_floor = 1
        self.main()

    def load_sounds(self):
        self.ball_hit_1a = pygame.mixer.Sound(c.sound_path("balls hit 1(a).wav"))
        self.ball_hit_1b = pygame.mixer.Sound(c.sound_path("balls hit 1(b).wav"))
        self.ball_hit_1c = pygame.mixer.Sound(c.sound_path("balls hit 1(c).wav"))
        self.ball_hit_2a = pygame.mixer.Sound(c.sound_path("balls hit 2(a).wav"))
        self.ball_hit_2b = pygame.mixer.Sound(c.sound_path("balls hit 2(b).wav"))
        self.ball_hit_2c = pygame.mixer.Sound(c.sound_path("balls hit 2(c).wav"))
        self.ball_hit_3a = pygame.mixer.Sound(c.sound_path("balls hit 3(a).wav"))
        self.ball_hit_3b = pygame.mixer.Sound(c.sound_path("balls hit 3(b).wav"))
        self.ball_hit_3c = pygame.mixer.Sound(c.sound_path("balls hit 3(c).wav"))

        self.into_pocket_a = pygame.mixer.Sound(c.sound_path("ball into pocket (a).wav"))
        self.into_pocket_b = pygame.mixer.Sound(c.sound_path("ball into pocket (b).wav"))
        self.into_pocket_c = pygame.mixer.Sound(c.sound_path("ball into pocket (c).wav"))

        self.hit_felt_loud1 = pygame.mixer.Sound(c.sound_path("Ball hits felt LOUD 1.wav"))
        self.hit_felt_loud2 = pygame.mixer.Sound(c.sound_path("Ball hits felt LOUD 2.wav"))
        self.hit_felt_loud3 = pygame.mixer.Sound(c.sound_path("Ball hits felt LOUD 3.wav"))
        self.hit_felt_soft1 = pygame.mixer.Sound(c.sound_path("Ball hits felt SOFT 1.wav"))
        self.hit_felt_soft2 = pygame.mixer.Sound(c.sound_path("Ball hits felt SOFT 3.wav"))
        self.hit_felt_soft3 = pygame.mixer.Sound(c.sound_path("Ball hits felt SOFT 5.wav"))

        self.whoosh = pygame.mixer.Sound(c.sound_path("whoosh.wav"))
        self.whoosh.set_volume(0.1)
        self.explosion = pygame.mixer.Sound(c.sound_path("explosion 1.wav"))
        self.shatter = pygame.mixer.Sound(c.sound_path("shield break.wav"))
        self.shatter.set_volume(0.6)

        self.door = pygame.mixer.Sound(c.sound_path("door.wav"))

        for soft in [self.hit_felt_soft3, self.hit_felt_soft1, self.hit_felt_soft2]:
            soft.set_volume(0.25)

        self.exploring = pygame.mixer.Sound(c.sound_path("exploring.mp3"))
        self.combat = pygame.mixer.Sound(c.sound_path("combat.mp3"))
        self.exploring_target_volume = 1
        self.exploring_volume = 1
        self.combat_target_volume = 0
        self.combat_volume = 0

        self.black_hole_suck = pygame.mixer.Sound(c.sound_path("black hole.wav"))
        self.black_hole_suck.set_volume(0.45)
        self.black_hole_ambient = pygame.mixer.Sound(c.sound_path("black hole ambient.wav"))
        self.black_hole_ambient.set_volume(0)
        self.black_hole_volume = 0
        self.since_black_hole = 999
        self.play_black_hole = False
        self.black_hole_target_volume = 0

    def load_image(self, path):
        if path not in self.image_dict:
            self.image_dict[path] = pygame.image.load(c.image_path(path))
        return self.image_dict[path]

    def hit_felt(self, velocity):
        mag = velocity.magnitude()
        sample = None
        if mag > 1000:
            mag = 1000
        if velocity.magnitude() > 250:
            sample = random.choice([self.hit_felt_loud3, self.hit_felt_loud1, self.hit_felt_loud2])
        elif velocity.magnitude() > 10:
            sample = random.choice([self.hit_felt_soft1, self.hit_felt_soft2, self.hit_felt_soft3])
        if sample:
            sample.set_volume((mag/1000)**1.5 + 0.1)
            sample.play()

    def into_pocket(self):
        to_play = random.choice([self.into_pocket_a, self.into_pocket_b, self.into_pocket_c])
        to_play.set_volume(0.5)
        to_play.play()

    def balls_hit(self, intensity):
        if intensity == 1:
            random.choice([self.ball_hit_3a, self.ball_hit_3b, self.ball_hit_3c]).play()
        elif intensity == 2:
            random.choice([self.ball_hit_1a, self.ball_hit_1b, self.ball_hit_1c]).play()
        elif intensity == 3:
            random.choice([self.ball_hit_2a, self.ball_hit_2b, self.ball_hit_2c]).play()

    def update_global(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(0)
        dt = self.clock.tick(c.FPS)/1000

        crossfade_speed = 1
        bh_factor = 1 - (self.play_black_hole*0.7)
        if self.exploring_target_volume*bh_factor < self.exploring_volume:
            self.exploring_volume = max(self.exploring_target_volume*bh_factor, self.exploring_volume - crossfade_speed*dt)
        elif self.exploring_target_volume*bh_factor > self.exploring_volume:
            self.exploring_volume = min(self.exploring_target_volume*bh_factor, self.exploring_volume + crossfade_speed*dt)
        if self.combat_target_volume*bh_factor < self.combat_volume:
            self.combat_volume = max(self.combat_target_volume*bh_factor, self.combat_volume - crossfade_speed*dt)
        elif self.combat_target_volume*bh_factor > self.combat_volume:
            self.combat_volume = min(self.combat_target_volume*bh_factor, self.combat_volume + crossfade_speed*dt)
        self.exploring.set_volume(self.exploring_volume*0.5)
        self.combat.set_volume(self.combat_volume)

        self.since_black_hole += dt
        if self.since_black_hole > 9 and self.play_black_hole:
            self.since_black_hole = 0
            self.black_hole_ambient.play()

        if self.play_black_hole:
            self.black_hole_target_volume = 1.0
        else:
            self.black_hole_target_volume = 0
        if self.black_hole_target_volume < self.black_hole_volume:
            self.black_hole_volume = max(self.black_hole_target_volume, self.black_hole_volume - crossfade_speed*dt)
        elif self.black_hole_target_volume > self.black_hole_volume:
            self.black_hole_volume = min(self.black_hole_target_volume, self.black_hole_volume + crossfade_speed*dt)
        self.black_hole_ambient.set_volume(self.black_hole_volume)

        return dt, events

    def main(self):
        lag = 0
        while True:
            dt, events = self.update_global()
            lag += dt
            times = 0
            while lag > 1/c.SIM_FPS:
                times += 1
                lag -= 1/c.SIM_FPS
                self.current_scene.update(1/c.SIM_FPS, events)
                if times > 3:
                    lag = 0
                    break
            self.current_scene.draw(self.screen, (0, 0))
            if self.current_scene.is_over:
                old_scene = self.current_scene
                self.current_scene = None
                self.current_scene = old_scene.next_scene()
            pygame.display.flip()


if __name__ == '__main__':
    Game()