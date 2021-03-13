from primitives import GameObject


class Scene(GameObject):
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.is_over = False

    def next_scene(self):
        return Scene

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        pass
