import pygame
import math

from primitives import PhysicsObject, Pose
import constants as c
from particle import Spark
import random
import time


class Ball(PhysicsObject):
    def __init__(self, game, x=0, y=0, radius=c.DEFAULT_BALL_RADIUS, drag_multiplicative= c.DEFAULT_BALL_MULT_DRAG, drag_constant = c.DEFAULT_BALL_CONSTANT_DRAG, max_speed = c.DEFAULT_BALL_MAX_SPEED):
        self.radius = radius
        self.mass = 1
        self.color = (255, 0, 0)  # This won't matter once we change drawing code
        super().__init__(game, (x, y), 0)
        self.load_back_surface()
        self.process_back_surface()
        self.generate_overlay()
        self.generate_shading()
        self.generate_shadow()
        self.surf = pygame.Surface((self.radius*2, self.radius*2))
        self.surf.set_colorkey(c.MAGENTA)
        self.initial_position = Pose((x, y), 0)
        self.drag_multiplicative = drag_multiplicative
        self.drag_constant = drag_constant
        self.max_speed = max_speed
        self._did_collide = False
        self.outline_hidden = False

    def process_back_surface(self):
        self.back_surface = pygame.transform.scale(self.back_surface, (self.radius*4, self.radius*4)).convert()
        noise = pygame.image.load(c.image_path("noise.png")).convert()
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
        self.back_surface = pygame.image.load(c.image_path(f"{random.choice([1, 2, 3, 4, 5, 6, 7, 8])}_ball.png"))

    def update(self, dt, events):
        super().update(dt, events)  # update position based on velocity, velocity based on acceleration

        self.drag(dt)

        self.update_collisions()

    def drag(self, dt):
        if(self.velocity.magnitude() > self.max_speed):
            self.velocity.scale_to(self.max_speed)
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
        mapTiles = self.game.current_scene.map.tiles_near(self.pose, self.radius*1.25);

        #check for collisions
        for ball in balls:
            if ball is self:
                continue
            if self._did_collide:
                return
            if ball._did_collide:
                continue
            if (self.pose - ball.pose).magnitude() < self.radius + ball.radius:
                #It Hit
                #print( (self.pose - ball.pose).magnitude() )

                self._did_collide = True;
                self.collide_with_other_ball_2(ball)
                #ball.collide_with_other_ball_2(self)
                break

        for mapTile in mapTiles:
            relative_pose = (self.map_coordinate_to_pose(mapTile) - self.pose)
            #if self._did_collide: Probably don't need or want this here
            #   return
            if (abs(relative_pose.x) > c.TILE_SIZE/2 + self.radius*.5 and abs(relative_pose.x) < c.TILE_SIZE/2 + self.radius*1.5 and \
                abs(relative_pose.y) > c.TILE_SIZE/2 + self.radius*.5 and abs(relative_pose.y) < c.TILE_SIZE/2 + self.radius*1.5 and mapTile.collidable):
                self.do_corner_collision(mapTile)
                continue
            if mapTile.collidable and (abs(relative_pose.x) < c.TILE_SIZE/2 + self.radius and abs(relative_pose.y) < c.TILE_SIZE/2 + self.radius):
                self.do_collision(mapTile)





        # TODO iterate through other balls and call self.collide_with_other_ball if colliding
        # TODO iterate through nearby map tiles and call self.collide_with_tile if colliding
        pass
    def do_collision(self, mapTile):
        print("wall");

        if(mapTile.down_bumper):
            self.velocity.y = abs(self.velocity.y)
        if (mapTile.up_bumper):
            self.velocity.y = abs(self.velocity.y) * -1
        if (mapTile.left_bumper):
            self.velocity.x = abs(self.velocity.x) * -1
        if (mapTile.right_bumper):
            self.velocity.x = abs(self.velocity.x)


    def do_corner_collision(self, mapTile):
        if not (mapTile.top_right_corner or mapTile.top_left_corner or mapTile.bottom_right_corner or mapTile.bottom_left_corner):
            self.do_collision(mapTile)
            return()

        print("wall_corner");

        return ()

    def map_coordinate_to_pose(self, mapTile):
        return(Pose(((mapTile.x * c.TILE_SIZE) + c.TILE_SIZE/2, mapTile.y * c.TILE_SIZE + c.TILE_SIZE/2 ) ,0)) #offset by tilezise /2 to get center

    def collide_with_other_ball_2(self, other):


        # Offset balls
        print(self.color)
        collision_normal = self.pose - other.pose
        offset_required = (collision_normal.magnitude() - (self.radius + other.radius) ) / 1.95
        collision_normal.scale_to(1)
        self.pose -= collision_normal * offset_required
        other.pose += collision_normal * offset_required

        spark_pose = self.pose - (self.pose - other.pose) * .5
        self.small_spark_explosion((spark_pose.x, spark_pose.y))
        self.game.current_scene.shake(10, other.pose - self.pose)

        relative_velocity = self.velocity - other.velocity;
        if(relative_velocity.magnitude() == 0):
            return


        other_relative_vector = collision_normal
        momemtum = relative_velocity * self.mass

        dot_product_vectors = collision_normal.x * relative_velocity.x + collision_normal.y * relative_velocity.y;

        energyRatio = math.sin( math.acos (dot_product_vectors/ (collision_normal.magnitude() * relative_velocity.magnitude()) ) )

        print(energyRatio)

        if energyRatio<0.01:
            energyRatio = 0.01
        if energyRatio>.99:
            energyRatio = .99


        #self_relative_momentum = energyRatio*momemtum
        other_relative_momentum = collision_normal*momemtum.magnitude() * ( (energyRatio-1) * -1)
        #other_relative_momentum = collision_normal*(momemtum.magnitude() - energyRatio*momemtum.magnitude())

        other_relative_velocity = other_relative_momentum * (1/other.mass)

        self_relative_momentum = momemtum + other_relative_momentum
        self_relative_velocity = self_relative_momentum * (1/self.mass)

        self.velocity = (self_relative_velocity + other.velocity) ;
        other.velocity = (other_relative_velocity*-1 + other.velocity) ;

    def collide_with_wall_corner(self, wall_pose, wall_tile):

        # Offset balls
        collision_normal = self.pose - wall_pose

        #NEED TO FIND OUT WHICH WALL CORNER AND MOVE POSE APPROPRIATELY
        if(wall_tile.top_right_corner)
            wall_pose.x += c.TILE_SIZE/2
            wall_pose.y -= c.TILE_SIZE/2
        if (wall_tile.top_left_corner)
            wall_pose.x -= c.TILE_SIZE / 2
            wall_pose.y -= c.TILE_SIZE / 2
        if (wall_tile.bottom_right_corner)
            wall_pose.x -= c.TILE_SIZE / 2
            wall_pose.y += c.TILE_SIZE / 2
        if (wall_tile.bottom_left_corner)
            wall_pose.x -= c.TILE_SIZE / 2
            wall_pose.y -= c.TILE_SIZE / 2

        offset_required = (collision_normal.magnitude() - (self.radius + c.TILE_SIZE/6)) / 1.9
        collision_normal.scale_to(1)

        dot_product_self = collision_normal.x * self.velocity.x + collision_normal.y * self.velocity.y;

        output_velocity_vector = (dot_product_self * collision_normal * 2 - self.velocity) * wall_tile.bounce_factor
        pass


    def collide_with_other_ball_3(self, other):
        self.small_spark_explosion((self.pose.x, self.pose.y))
        self.game.current_scene.shake(10, other.pose - self.pose)

        to_other = other.pose - self.pose
        relative_velocity = other.velocity - self.velocity
        other.velocity -= relative_velocity
        self.velocity -= relative_velocity

        velocity_angle = math.atan2(self.velocity.y, self.velocity.x)
        to_other_angle = math.atan2(to_other.y, to_other.x)
        diff = to_other_angle - velocity_angle
        diff = diff % (2*math.pi)
        print(diff* 180/math.pi)

        energy_transfer = abs(math.sin(diff))
        collision_normal = to_other.copy()
        collision_normal.scale_to(1)
        dot_product_vectors = collision_normal.x * self.velocity.x + collision_normal.y * self.velocity.y;

        energy_transfer = math.sin( math.acos(dot_product_vectors / (collision_normal.magnitude() * self.velocity.magnitude())))
        energy_transfer = (energy_transfer -1)*-1
        energy_transfer = .01

        magnitude = self.velocity.magnitude()
        other_new = to_other.copy()
        other_new.scale_to(magnitude * energy_transfer)
        vel_change = other_new.copy()
        vel_change.scale_to(magnitude * (1 - energy_transfer))
        other.velocity = other_new
        print(self.velocity)
        self.velocity -= vel_change
        print(self.velocity)
        print(energy_transfer)
        print()

        other.velocity += relative_velocity
        self.velocity += relative_velocity


#in a direction
#relative output veloctity ball 2  = (original velocity x 2


        pass

    def collide_with_other_ball(self, other):
        # Offset balls
        collision_normal = self.pose - other.pose
        offset_required = (collision_normal.magnitude() - (self.radius + other.radius) ) / 1.9
        collision_normal.scale_to(1)

        self_output_velocity = (self.velocity * ((self.mass - other.mass)/(self.mass + other.mass)) ) + ( other.velocity * ((2 * other.mass)/(self.mass + other.mass)) )
        other_output_velocity = (self.velocity * ((2 * self.mass)/(self.mass + other.mass)) ) + (other.velocity * ((other.mass - self.mass)/(other.mass + self.mass)) )
        #TOTAL ELASTIC
        #Distribute a % of inertia

        elastic_factor = 1


        self_velocity_vector = self.velocity.copy()
        self_velocity_vector.scale_to(1)

        other_velocity_vector = other.velocity.copy()
        other_velocity_vector.scale_to(1)

        dot_product_self = collision_normal.x * self.velocity.x + collision_normal.y * self_velocity_vector.y;
        self_output_velocity_vector = self_velocity_vector - collision_normal * 2 * dot_product_self

        dot_product_other = collision_normal.x * other.velocity.x + collision_normal.y * other_velocity_vector.y;
        other_output_velocity_vector = other_velocity_vector + collision_normal * 2 * dot_product_self

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

        if c.DEBUG:
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

        if not self.outline_hidden:
            pygame.draw.circle(screen, c.BLACK, (x+self.radius, y+self.radius), self.radius, 2)

    def draw_shadow(self, screen, offset=(0, 0)):
        x, y = self.pose.get_position()
        x += offset[0] - self.radius
        y += offset[1] - self.radius + self.radius//2
        screen.blit(self.shadow, (x, y))

    def small_spark_explosion(self, position):
        for i in range(10):
            spark = Spark(self.game, *position)
            self.game.current_scene.particles.append(spark)


class Shelled(Ball):
    def __init__(self, game, inner_ball, **kwargs):
        super().__init__(game, **kwargs)
        self.inner_ball = inner_ball
        self.radius = self.inner_ball.radius * 1.5
        self.shell_surf = pygame.Surface((self.radius*2, self.radius*2))
        self.shell_surf.fill(c.MAGENTA)
        pygame.draw.circle(self.shell_surf, (200, 220, 255), (self.radius, self.radius), self.radius)
        self.shell_surf.set_colorkey(c.MAGENTA)
        self.shell_surf.set_alpha(60)
        self.inner_ball.outline_hidden = True
        self.twinkle_surf = self.shell_surf.copy()
        self.twinkle_surf.fill(c.BLACK)
        pygame.draw.circle(self.twinkle_surf, c.WHITE, (self.radius*1.4, self.radius*0.55), self.radius*0.25)
        pygame.draw.circle(self.twinkle_surf, c.WHITE, (self.radius * 1.7, self.radius * 0.7), self.radius * 0.1)
        self.twinkle_surf.set_alpha(100)
        self.twinkle_surf.set_colorkey(c.BLACK)
        self.broken = False

    def update(self, dt, events):
        super().update(dt, events)
        self.inner_ball.pose = self.pose.copy()

    def draw(self, surf, offset=(0, 0)):
        self.inner_ball.draw(surf, offset=offset)
        x = self.pose.x + offset[0] - self.shell_surf.get_width()//2
        y = self.pose.y + offset[1] - self.shell_surf.get_height()//2
        surf.blit(self.shell_surf, (x, y))
        if not self.outline_hidden:
            pygame.draw.circle(surf, c.BLACK, (x+self.radius, y+self.radius), self.radius, 2)

        diff = self.pose - self.initial_position
        tx = 1 * math.sin(diff.x/7)
        ty = 1 * math.cos(diff.y/7)
        surf.blit(self.twinkle_surf, (x + tx, y + ty))

    def draw_shadow(self, screen, offset=(0, 0)):
        offset = (offset[0], offset[1] + self.inner_ball.radius*0.25)
        self.inner_ball.draw_shadow(screen, offset=offset)