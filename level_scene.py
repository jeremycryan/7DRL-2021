from scene import Scene
from ball import Ball, Shelled
from player import Player
from map import Map
from camera import Camera
import pygame


class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.player = Player(game, 200, 500)
        self.balls = [self.player,
                      Ball(self.game, 300, 250)]
                      # Ball(self.game, 400, 200, 50),
                      # Ball(self.game, 550, 150),
                      # Shelled(self.game, Ball(self.game), x=500, y=500)]
        self.current_ball = self.player
        self.current_ball.turn_in_progress = True
        self.map = Map(self.game)
        self.particles = []
        self.floor_particles = []
        self.camera = Camera(game, self.current_room())

    def shake(self, amt, pose=None):
        self.camera.shake(amt, pose)

    def update_current_ball(self):
        if not self.current_ball.turn_in_progress:
            index = (self.balls.index(self.current_ball) + 1) % len(self.balls)
            self.current_ball = self.balls[index]
            self.current_ball.start_turn()

    def no_enemies(self):
        for ball in self.balls:
            if ball is not self.player:
                return False
        return True

    def all_balls_below_speed(self, speed=5):
        for ball in self.balls:
            if ball.velocity.magnitude() > speed:
                return False
        return True

    def update(self, dt, events):
        for ball in self.balls:
            ball._did_collide = False;
        for ball in self.balls:
            ball.update(dt, events)
        self.update_current_ball()
        for ball in self.balls[:]:
            if ball.has_sunk():
                self.balls.remove(ball)
        for particle in self.particles:
            particle.update(dt, events)
        for particle in self.particles[:]:
            if particle.dead:
                self.particles.remove(particle)
        for particle in self.floor_particles:
            particle.update(dt, events)
        for particle in self.floor_particles[:]:
            if particle.dead:
                self.floor_particles.remove(particle)
        self.map.update(dt, events)
        self.camera.update(dt, events)
        self.camera.object_to_track = self.current_room()

    def draw(self, surface, offset=(0, 0)):
        surface.fill((30, 80, 30))
        offset = self.camera.add_offset(offset)
        self.map.draw(surface, offset=offset)
        for particle in self.floor_particles:
            particle.draw(surface, offset=offset)
        for ball in self.balls:
            ball.draw_shadow(surface, offset=offset)
        for ball in self.balls:
            ball.draw(surface, offset=offset)
        for particle in self.particles:
            particle.draw(surface, offset=offset)

    def current_room(self):
        return self.map.get_at_pixels(*self.player.pose.get_position())