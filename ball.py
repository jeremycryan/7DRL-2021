import pygame

from primitives import PhysicsObject, Pose
import constants as c


class Ball(PhysicsObject):
    def __init__(self, game, x=0, y=0, radius=c.DEFAULT_BALL_RADIUS):
        self.radius = radius
        self.weight = 1
        self.color = (255, 0, 0)  # This won't matter once we change drawing code
        self.load_back_surface()
        self.process_back_surface()
        super().__init__(game, (x, y), 0)
        self.generate_overlay()
        self.generate_shading()
        self.generate_shadow()
        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.surf.set_colorkey(c.MAGENTA)
        self.initial_position = Pose((x, y), 0)

    def process_back_surface(self):
        self.back_surface = pygame.transform.scale(self.back_surface, (self.radius*4, self.radius*4))
        noise = pygame.image.load(c.image_path("noise.png"))
        x_times = int(self.back_surface.get_width() / noise.get_width()) + 1
        y_times = int(self.back_surface.get_height() / noise.get_height()) + 1
        for x in range(x_times):
            for y in range(y_times):
                x0 = x*noise.get_width()
                y0 = y*noise.get_height()
                self.back_surface.blit(noise, (x0, y0), special_flags=pygame.BLEND_MULT)

    def generate_overlay(self):
        self.overlay = pygame.Surface((2*self.radius, 2*self.radius))
        self.overlay.fill(c.MAGENTA)
        pygame.draw.circle(self.overlay, c.WHITE, (self.radius, self.radius), self.radius)
        self.overlay.set_colorkey(c.WHITE)

    def generate_shading(self):
        self.shading = pygame.Surface((2*self.radius, 2*self.radius))
        self.shading.fill(c.WHITE)
        s_height = self.radius
        s_y = self.shading.get_height()//2 - s_height//2
        pygame.draw.circle(self.shading, (150, 150, 150), (self.radius, self.radius), self.radius)
        pygame.draw.ellipse(self.shading, c.WHITE, (0, s_y, self.radius*2, s_height))
        pygame.draw.rect(self.shading, c.WHITE, (0, 0, 2*self.radius, self.radius))

    def generate_shadow(self):
        self.shadow = pygame.Surface((2*self.radius, 2*self.radius))
        self.shadow.fill(c.MAGENTA)
        pygame.draw.circle(self.shadow, c.BLACK, (self.radius, self.radius), self.radius)
        self.shadow.set_alpha(50)
        self.shadow.set_colorkey(c.MAGENTA)

    def load_back_surface(self):
        # Load scrolly image
        self.back_surface = pygame.Surface((self.radius*2, self.radius*2))
        self.back_surface.fill((50, 80, 255))

    def update(self, dt, events):
        super().update(dt, events)  # update position based on velocity, velocity based on acceleration

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

        off_from_initial = self.pose - self.initial_position

        for off in (0, 0), (-1, 0), (-1, -1), (0, -1):
            x0 = off_from_initial.x % self.back_surface.get_width() + off[0]*self.back_surface.get_width()
            y0 = off_from_initial.y % self.back_surface.get_height() + off[1]*self.back_surface.get_width()
            self.surf.blit(self.back_surface, (x0, y0))

        self.surf.blit(self.overlay, (0, 0))
        x -= self.radius
        y -= self.radius
        screen.blit(self.surf, (x, y))
        screen.blit(self.shading, (x, y), special_flags=pygame.BLEND_MULT)

        pygame.draw.circle(screen, c.BLACK, (x+self.radius, y+self.radius), self.radius, 2)

    def draw_shadow(self, screen, offset=(0, 0)):
        x, y = self.pose.get_position()
        x += offset[0] - self.radius
        y += offset[1] - self.radius + self.radius//2
        screen.blit(self.shadow, (x, y))