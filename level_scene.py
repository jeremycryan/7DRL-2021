from scene import Scene
from ball import Ball
from player import Player


class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.player = Player(200, 200)
        self.balls = [Ball(self.game, 50, 50, 20),
                      Ball(self.game, 100, 100, 30),
                      Ball(self.game, 150, 50, 20)]

    def update(self, dt, events):
        self.player.update(dt, events)
        for ball in self.balls:
            ball.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((0, 0, 0))
        self.player.draw(surface, offset=offset)
        for ball in self.balls:
            ball.draw(surface, offset=offset)
