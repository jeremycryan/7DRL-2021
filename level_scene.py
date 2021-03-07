from scene import Scene
from ball import Ball
from player import Player


class LevelScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.player = Player(game, 200, 500)
        self.balls = [self.player,
                      Ball(self.game, 100, 50),
                      Ball(self.game, 200, 100, 50),
                      Ball(self.game, 350, 50)]

    def update(self, dt, events):
        for ball in self.balls:
            ball._did_collide = False;
        for ball in self.balls:
            ball.update(dt, events)
        pass

    def draw(self, surface, offset=(0, 0)):
        surface.fill((30, 80, 30))
        for ball in self.balls:
            ball.draw_shadow(surface, offset=offset)
        for ball in self.balls:
            ball.draw(surface, offset=offset)
