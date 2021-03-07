import pygame

from primitives import PhysicsObject, Pose


class Ball(PhysicsObject):
    def __init__(self, game, x=0, y=0, radius=20):
        self.radius = radius
        self.weight = 1
        self.color = (255, 0, 0)  # This won't matter once we change drawing code
        super().__init__(game, (x, y), 0)

    def update(self, dt, events):
        super().update(dt, events)  # update position based on velocity, velocity based on acceleration
        # TODO (Jeremy) update offset on inner surf to simulate ball rolling animation

        self.update_collisions()

    def update_collisions(self):
        # TODO iterate through other balls and call self.collide_with_other_ball if colliding
        # TODO iterate through nearby map tiles and call self.collide_with_tile if colliding
        pass

    def collide_with_other_ball(self, other):
        # TODO implement this
        # Don't forget to somehow flag this collision so it doesn't happen again this frame when other is updated
        pass

    def collide_with_tile(self, tile):
        # TODO
        pass

    def knock(self, cue, angle, power):
        # TODO implement this
        # Angle should be the angle, in degrees counterclockwise from --> right -->
        # Power should be a float from 0-100 indicating how hard you're hitting. This might not map 1:1 to velocity
        # depending on the Cue object.
        speed = cue.power_to_speed(power=power, ball=self)
        velocity_vector = Pose((speed, 0), 0)
        velocity_vector.rotate_position(angle)
        self.velocity += velocity_vector

    def draw(self, screen, offset=(0, 0)):
        x, y = self.pose.get_position()
        x += offset[0]
        y += offset[1]
        pygame.draw.circle(screen, self.color, (x, y), self.radius)