from scene import Scene
from ball import Ball
from player import Player
from map import Map
from camera import Camera


class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.player = Player(game, 200, 500)
        self.camera = Camera(game, self.player)
        self.balls = [self.player,
                      Ball(self.game, 100, 50),
                      Ball(self.game, 200, 100, 50),
                      Ball(self.game, 350, 50)]
        self.map = Map(self.game)

    def update(self, dt, events):
        for ball in self.balls:
            ball._did_collide = False;
        for ball in self.balls:
            ball.update(dt, events)
        self.map.update(dt, events)
        self.camera.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((30, 80, 30))
        offset = self.camera.add_offset(offset)
        self.map.draw(surface, offset=offset)
        for ball in self.balls:
            ball.draw_shadow(surface, offset=offset)
        for ball in self.balls:
            ball.draw(surface, offset=offset)
