import pygame
import math

from primitives import PhysicsObject, Pose
import constants as c


class Ball(PhysicsObject):
    def __init__(self, game, x=0, y=0, radius=c.DEFAULT_BALL_RADIUS, drag_multiplicative= c.DEFAULT_BALL_MULT_DRAG, drag_constant = c.DEFAULT_BALL_CONSTANT_DRAG):
        self.radius = radius
        self.mass = 1
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
        self.drag_multiplicative = drag_multiplicative
        self.drag_constant = drag_constant
        self._did_collide = False

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

        self.drag(dt)

        self.update_collisions()

    def drag(self, dt):

        self.velocity -= self.velocity * self.drag_multiplicative * dt;
        _temp_velocity = self.velocity.copy();
        _temp_velocity.scale_to(1);
        if(self.velocity.x > 0):
            posX = True
        else:
            posX = False
        if (self.velocity.y > 0):
            posY = True
        else:
            posY = False
        self.velocity -= _temp_velocity * self.drag_constant * dt;


        if ( (self.velocity.x > 0 and not posX) or (self.velocity.y > 0 and not posY) ):
            self.velocity *= 0;

    def update_collisions(self):

        balls = self.game.current_scene.balls;

        #check for collisions
        for ball in balls:
            if ball is self:
                continue
            if ball._did_collide:
                continue
            if (self.pose - ball.pose).magnitude() < self.radius + ball.radius:
                #It Hit
                print( (self.pose - ball.pose).magnitude() )

                self._did_collide = True;
                #self.collide_with_other_ball(ball) Don't need this, do both in one
                ball.collide_with_other_ball(self)
                break
        # TODO iterate through other balls and call self.collide_with_other_ball if colliding
        # TODO iterate through nearby map tiles and call self.collide_with_tile if colliding
        pass

    def collide_with_other_ball(self, other):
        # Offset balls
        collision_normal = self.pose - other.pose
        offset_required = (collision_normal.magnitude() - (self.radius + other.radius) ) / 1.95
        collision_normal.scale_to(1)

        self_output_velocity = (self.velocity * ((self.mass - other.mass)/(self.mass + other.mass)) ) + ( other.velocity * ((2 * other.mass)/(self.mass + other.mass)) )
        other_output_velocity = (self.velocity * ((2 * self.mass)/(self.mass + other.mass)) ) + (other.velocity * ((other.mass - self.mass)/(other.mass + self.mass)) )
        #TOTAL ELASTIC
        #Distribute a % of inertia

        elastic_factor = .9

        self.velocity = (self_output_velocity * (1/self.mass) * elastic_factor + other_output_velocity * (1/other.mass) * (1-elastic_factor) ) * self.mass
        other.velocity = (other_output_velocity * (1/other.mass) * elastic_factor + self_output_velocity * (1/self.mass)  * (1-elastic_factor) ) * other.mass

        pass

    def collide_with_tile(self, tile):
        # TODO

        # Offset balls
        collision_normal = self.pose - other.pose
        offset_required = (collision_normal.magnitude() - (self.radius + other.radius)) / 1.95
        collision_normal.scale_to(1)

        self.pose -= collision_normal * offset_required
        other.pose += collision_normal * offset_required

        # Change velocities
        self_velocity_vector = self.velocity.copy()
        self_velocity_vector.scale_to(1)

        other_velocity_vector = other.velocity.copy()
        other_velocity_vector.scale_to(1)

        collision_normal *= 1;

        dot_product_self = collision_normal.x * self.velocity.x + collision_normal.y * self_velocity_vector.y;
        self_output_velocity_vector = self_velocity_vector - collision_normal * 2 * dot_product_self

        dot_product_other = collision_normal.x * other.velocity.x + collision_normal.y * other_velocity_vector.y;
        other_output_velocity_vector = other_velocity_vector + collision_normal * 2 * dot_product_self

        print(self.velocity.magnitude())
        # INERTIA CALCULATIONS
        self_inertia = self.velocity * self.mass
        other_inertia = other.velocity * other.mass
        inertia_total = self_inertia + other_inertia

        inertia_unit_vector = inertia_total.copy()
        inertia_unit_vector = inertia_unit_vector.scaleto()
        inertia_ratio = self_inertia / other_inertia

        self.velocity = self_output_velocity_vector * self.velocity.magnitude()
        other.velocity = other_output_velocity_vector * other.velocity.magnitude()

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

        for tile in self.game.current_scene.map.tiles_near(self.pose, self.radius):
            pygame.draw.rect(screen, self.color, (tile.x * c.TILE_SIZE + offset[0], tile.y * c.TILE_SIZE + offset[1], c.TILE_SIZE, c.TILE_SIZE), 1)

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