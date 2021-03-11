import pygame
import math

from primitives import PhysicsObject, Pose
import constants as c
from particle import Spark, SmokeBit
import random
from cue import BasicCue
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
        self._did_collide_wall = False
        self.outline_hidden = False
        self.rotational_velocity = Pose((0, 0), 0)
        self.since_smoke = 0
        self.can_collide = True
        self.tractor_beam_target = None
        self.can_be_sunk = True
        self.target_alpha = 255
        self.target_scale = 1
        self.alpha = 255
        self.scale = 1
        self.sunk = False
        self.turn_in_progress = False
        self.turn_phase = c.BEFORE_HIT
        self.is_player = False
        self.pointer = pygame.image.load(c.image_path("pointer.png"))
        self.pointer.set_colorkey(c.BLACK)

    def start_turn(self):
        self.turn_in_progress = True
        self.turn_phase = c.BEFORE_HIT
        self.take_turn()

    def take_turn(self):
        player = self.game.current_scene.player
        relative_position = self.pose - player.pose

        to_player_degrees = math.degrees(math.atan2(relative_position.y, -relative_position.x))
        max_offset_angle = math.degrees(math.sin( (self.radius + player.radius )/ relative_position.magnitude()) )
        relative_player_max_movement_angle = 90 - max_offset_angle

        current_room = self.game.current_scene.current_room();
        pockets = current_room.pockets

        #ORDERS POCKETS BY LESS ANGLE NEEDED
        #pockets.sort(key=lambda pocket: abs(math.degrees(math.atan2(player.pose.x - pocket.pose.x, player.pose.y - pocket.pose.y)) - to_player_degrees)   )
        pockets.sort(key=lambda pocket: abs(math.degrees(math.atan2(player.pose.y - pocket.pose.y, -player.pose.x + pocket.pose.x)) - to_player_degrees)   )

        #rounded_to_map_player_pose  = self.round_to_map_coordinate(player.pose)

        #CHECK IF POCKET IS VALID (WALLS) HERE

        is_wall = True
        found_pocket = False
        desired_pocket = -1
        wall_check_success = True;
        while is_wall:
            desired_pocket += 1
            if desired_pocket>= len(pockets):
                wall_check_success = False
                #print("BREAK, is_wall = " + str(is_wall))
                break
            is_wall = False
            current_step = 0

            relative_position_player_to_pocket = player.pose - pockets[desired_pocket].pose
            _scanner = relative_position_player_to_pocket.copy()
            _scanner *= -1
            _scanner.scale_to(1)

            while current_step < relative_position_player_to_pocket.magnitude() - c.TILE_SIZE and not is_wall:
                to_test_pose = player.pose +(_scanner * current_step)
                to_test_pose = self.round_to_map_coordinate(to_test_pose)

                #test_tile = self.game.current_scene.map.coordinate_collidable(to_test_pose.x, to_test_pose.y)
                #is_wall = test_tile.collidable

                is_wall = current_room.coordinate_collidable(to_test_pose.x, to_test_pose.y)
                #if(is_wall):
                    #print("FOUND WALL")

                current_step += c.TILE_SIZE/2

        #print("DESIRED POCKET NUMBER " + str(desired_pocket))

        goal_pocket_angle =  math.degrees(math.atan2(relative_position_player_to_pocket.y, -relative_position_player_to_pocket.x))

        goal_pocket_angle = goal_pocket_angle - to_player_degrees;

        internal_triangle_height = math.sin(math.radians(goal_pocket_angle)) * (self.radius + player.radius)
        goal_offset_angle = math.degrees(math.atan2(internal_triangle_height, relative_position.magnitude() - math.cos(math.radians(goal_pocket_angle)) * (self.radius + player.radius)) )

        if(goal_offset_angle> c.AI_MAX_ANGLE_REDUCTION):
            goal_offset_angle = c.AI_MAX_ANGLE_REDUCTION
        elif(goal_offset_angle< -c.AI_MAX_ANGLE_REDUCTION):
            goal_offset_angle = -c.AI_MAX_ANGLE_REDUCTION

        #print(goal_offset_angle)


        self.knock(BasicCue(), to_player_degrees - goal_offset_angle, 120)
        #MAYBE MAKE 3 DIIFRENT VERSIONS AND HAVE EACH BALL PICK ONE?

        #THE ABOVE IS ESENTIALLY ANGLE CORRECTION CODE, WE CAN USE THIS WHEN CALUCLATING WALL BOUNCES...

        #POCKET ORDERING CODE:
        #ONLY RUN CURRENT CODE FOR "IMPACT CONE" POCKETS
        #CURRENT CODE (GETS DIRECT SHOT VALID POCKETS AND ORDERS THEM)
        #HAVE THE CURRENT CODE ALSO CHECK FOR CROSSING WALLS FROM EMEMY TO PLAYER, NOT JUST PLAYER TO WALL
        #ATTEMPT BOUNCE SHOTS




        self.turn_phase = c.AFTER_HIT

    def round_to_map_coordinate(self, pose):
        _pose = pose.copy()
        _pose.x = round(_pose.x / c.TILE_SIZE)
        _pose.y = round(_pose.y / c.TILE_SIZE)
        return(_pose)

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

    def is_completely_in_room(self):
        for tile in self.game.current_scene.map.tiles_near(self.pose, self.radius):
            if tile.key not in [c.EMPTY, c.POCKET]:
                return False
        return True

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
        if self.game.current_scene.all_balls_below_speed() and self.turn_in_progress and self.turn_phase == c.AFTER_HIT:
            self.turn_in_progress = False
            self.turn_phase = c.BEFORE_HIT

        if self.tractor_beam_target:
            diff = self.tractor_beam_target - self.pose
            self.pose += diff*dt * 5

            if (self.tractor_beam_target - self.pose).magnitude() < 2:
                if self.target_alpha < self.alpha:
                    self.alpha -= 250*dt
                if self.target_scale < self.scale:
                    self.scale -= dt*1.2 - (self.target_scale - self.scale)*3*dt
                if self.alpha < 1:
                    self.sink_for_real()
                    return
            return

        super().update(dt, events)  # update position based on velocity, velocity based on acceleration

        self.drag(dt)
        self.since_smoke += dt
        period = 0.04
        while self.since_smoke > period:
            min_vel = 350
            max_vel = 500
            mag = self.velocity.magnitude()
            if mag > min_vel and not self.tractor_beam_target:
                num = min((mag - min_vel)/(max_vel - min_vel), 1) * 5
                self.make_smoke((self.pose.x, self.pose.y), int(num))
            self.since_smoke -= period

        self.update_collisions()

        #ROLL DELAY CODE
        if(self.velocity.magnitude() + self.rotational_velocity.magnitude() != 0):
            _factor_weight = self.velocity.magnitude()/(self.velocity.magnitude() + self.rotational_velocity.magnitude())
        else:
            _factor_weight = 0
        _temp_velocity = self.velocity.copy()
        _factor = c.TABLE_FRICTION_BALL_SPIN_RATIO * (_factor_weight ** 2)
        _temp_velocity.scale_to(self.rotational_velocity.magnitude() * _factor ** dt + self.velocity.magnitude() * (1 - _factor** dt))

        self.rotational_velocity = _temp_velocity
        self.initial_position += (self.velocity-self.rotational_velocity) * dt
        if(self.rotational_velocity.magnitude() < c.MIN_ROTATIONAL_VELOCITY):
            self.rotational_velocity *=0


    def drag(self, dt):
        if(self.velocity.magnitude() > self.max_speed):
            self.velocity.scale_to(self.max_speed)
        self.velocity -= self.velocity * self.drag_multiplicative * dt;
        _temp_velocity = self.velocity.copy();
        _temp_velocity.scale_to(1);
        # if(self.velocity.x > 0):
        #     posX = True
        # else:
        #     posX = False
        # if (self.velocity.y > 0):
        #     posY = True
        # else:
        #     posY = False

        self.velocity -= _temp_velocity * self.drag_constant * dt;

        _drag_factor = _temp_velocity * self.drag_constant * dt;


        #if ((self.velocity.x > 0 and not posX) or (self.velocity.x < 0 and posX) or (self.velocity.y > 0 and not posY) or (self.velocity.y < 0 and posY) ):
        #    self.velocity = Pose((0,0),0);

        if(_drag_factor.magnitude() >= self.velocity.magnitude() ):
            self.velocity = Pose((0,0),0)



    def update_collisions(self):
        if not self.can_collide:
            return

        balls = self.game.current_scene.balls;
        mapTiles = self.game.current_scene.map.tiles_near(self.pose, self.radius*1);

        for pocket in self.game.current_scene.current_room().pockets:
            if pocket.can_swallow(self) and self.can_be_sunk:
                pocket.swallow(self)
                return

        #check for collisions
        for ball in balls:
            if ball is self:
                continue
            if ball.is_player and ball.is_player:
                continue
            if not ball.can_collide:
                continue
            if self._did_collide:
                return
            if ball._did_collide:
                continue
            total_radius = self.radius + ball.radius

            # Abs and conditionals are fast. Check this first to save time
            if (abs(self.pose.x - ball.pose.x) > total_radius) or (abs(self.pose.y - ball.pose.y > total_radius)):
                continue
            if (self.pose - ball.pose).magnitude() < total_radius:
                #It Hit
                #print( (self.pose - ball.pose).magnitude() )

                self._did_collide = True;
                self.collide_with_other_ball_2(ball)
                #ball.collide_with_other_ball_2(self)
                break

        for mapTile in mapTiles: #CORNERS FIRST

            if not (mapTile.top_right_corner or mapTile.top_left_corner or mapTile.bottom_right_corner or mapTile.bottom_left_corner):
                continue

            relative_pose = (self.map_coordinate_to_pose(mapTile) - self.pose)

            if mapTile.collidable and (abs(relative_pose.x) < c.TILE_SIZE/2 + self.radius and abs(relative_pose.y) < c.TILE_SIZE/2 + self.radius):
                if(mapTile.top_left_corner):
                    temp_pose = relative_pose.copy()
                    temp_pose.x += c.TILE_SIZE/2
                    temp_pose.y += c.TILE_SIZE/2
                    if(temp_pose.magnitude()< c.TILE_SIZE + self.radius):
                        self._did_collide_wall = True;
                        self.collide_with_wall_corner_2(temp_pose, mapTile)
                elif(mapTile.top_right_corner):
                    temp_pose = relative_pose.copy()
                    temp_pose.x -= c.TILE_SIZE / 2
                    temp_pose.y += c.TILE_SIZE / 2
                    if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                        self._did_collide_wall = True;
                        self.collide_with_wall_corner_2(temp_pose, mapTile)
                elif(mapTile.bottom_left_corner):
                    temp_pose = relative_pose.copy()
                    temp_pose.x += c.TILE_SIZE / 2
                    temp_pose.y -= c.TILE_SIZE / 2
                    if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                        self._did_collide_wall = True;
                        self.collide_with_wall_corner_2(temp_pose, mapTile)
                elif(mapTile.bottom_right_corner):
                    temp_pose = relative_pose.copy()
                    temp_pose.x -= c.TILE_SIZE / 2
                    temp_pose.y -= c.TILE_SIZE / 2
                    if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                        self._did_collide_wall = True;
                        self.collide_with_wall_corner_2(temp_pose, mapTile)

        mapTiles = self.game.current_scene.map.tiles_near(self.pose, self.radius*1);
        for mapTile in mapTiles:
            if (mapTile.top_right_corner or mapTile.top_left_corner or mapTile.bottom_right_corner or mapTile.bottom_left_corner):
                continue
            relative_pose = (self.map_coordinate_to_pose(mapTile) - self.pose)

            if mapTile.collidable and ((abs(relative_pose.x) < c.TILE_SIZE / 2 + self.radius and abs(relative_pose.y) < c.TILE_SIZE / 2) or (abs(relative_pose.x) < c.TILE_SIZE / 2  and abs(relative_pose.y) < c.TILE_SIZE / 2 + self.radius)):
                self._did_collide_wall = True;
                self.do_collision(mapTile)


        if (self._did_collide_wall):
            self._did_collide_wall = False
            if (self.velocity.magnitude() > c.MIN_BOUNCE_REDUCTION_SPEED or c.WALL_BOUNCE_FACTOR):
                self.velocity.scale_to(self.velocity.magnitude() * c.WALL_BOUNCE_FACTOR)
            self.game.current_scene.shake(8 * self.velocity.magnitude() / 500, pose=self.velocity)

        # TODO iterate through other balls and call self.collide_with_other_ball if colliding
        # TODO iterate through nearby map tiles and call self.collide_with_tile if colliding
        pass

    def do_collision(self, mapTile):
        #return()
        #print("wall");
        self.game.current_scene.shake(8 * self.velocity.magnitude()/500, pose=self.velocity)

        #shift pose away from wall
        #relative_position = self.pose - self.map_coordinate_to_pose(mapTile)

        if mapTile.down_bumper :#and relative_position.y - self.radius - c.COLLIDER_SIZE >0 :
            self.velocity.y = abs(self.velocity.y)
            self.pose.y = (self.map_coordinate_to_pose(mapTile).y + c.TILE_SIZE/2) + self.radius
        elif mapTile.up_bumper :#and relative_position.y + self.radius + c.COLLIDER_SIZE <0:
            self.velocity.y = abs(self.velocity.y) * -1
            self.pose.y = (self.map_coordinate_to_pose(mapTile).y - c.TILE_SIZE/2) - self.radius
        elif mapTile.left_bumper :#and relative_position.x + self.radius + c.COLLIDER_SIZE <0:
            self.velocity.x = abs(self.velocity.x) * -1
            self.pose.x = (self.map_coordinate_to_pose(mapTile).x - c.TILE_SIZE/2) - self.radius
        elif mapTile.right_bumper :#and relative_position.x - self.radius - c.COLLIDER_SIZE >0:
            self.velocity.x = abs(self.velocity.x)
            self.pose.x = (self.map_coordinate_to_pose(mapTile).x + c.TILE_SIZE/2) + self.radius

        if(self.velocity.magnitude() < c.MIN_WALL_BOUNCE_SPEED):
            self.velocity.scale_to(c.MIN_WALL_BOUNCE_SPEED)
        if(self.velocity.magnitude() > c.MIN_BOUNCE_REDUCTION_SPEED or mapTile.bounce_factor > 1):
            self.velocity.scale_to(self.velocity.magnitude() * mapTile.bounce_factor)

    def do_corner_collision(self, mapTile):
        #if (mapTile.top_right_corner or mapTile.top_left_corner or mapTile.bottom_right_corner or mapTile.bottom_left_corner):
        #    print("wall_corner_fail");
        #    self.do_collision(mapTile)
        #    return()

        self.collide_with_wall_corner(self.map_coordinate_to_pose(mapTile), mapTile)

        return ()

    def map_coordinate_to_pose(self, mapTile):
        return(Pose(((mapTile.x * c.TILE_SIZE) + c.TILE_SIZE/2, mapTile.y * c.TILE_SIZE + c.TILE_SIZE/2 ) ,0)) #offset by tilezise /2 to get center

    def collide_with_other_ball_2(self, other):


        # Offset balls
        collision_normal = self.pose - other.pose
        collision_normal_unscaled = collision_normal.copy()
        #offset_required = (collision_normal.magnitude() - (self.radius + other.radius) ) / 1.95
        #collision_normal.scale_to(1)
        #self.pose -= collision_normal * offset_required
        #other.pose += collision_normal * offset_required

        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        collision_normal.scale_to(1)
        velocity_vector = self.velocity.copy()
        velocity_vector.scale_to(1)
        # self.pose += velocity_vector * (offset_required * math.cos(math.atan2(velocity_vector.y-collision_normal.y, velocity_vector.x-collision_normal.x)))
        dot_product_self_norm = collision_normal.x * velocity_vector.x + collision_normal.y * velocity_vector.y;

        angle_vel = math.acos(dot_product_self_norm / (collision_normal.magnitude() * velocity_vector.magnitude()))

        angle_b = math.asin((math.sin(angle_vel) / (self.radius + other.radius)) * collision_normal_unscaled.magnitude())
        angle_c = math.pi - (angle_b + angle_vel)
        interpolated_offset = ((self.radius + other.radius) / math.sin(angle_vel)) * math.sin(angle_c)
        # print("OFFSET :" + str(interpolated_offset) + "    angle C: " + str(math.degrees(angle_c)) + "    angle vel: " + str(math.degrees(angle_vel)))

        self.pose -= velocity_vector * abs(interpolated_offset) * (self.velocity.magnitude()/(self.velocity.magnitude() + other.velocity.magnitude()))
        other.pose += velocity_vector * abs(interpolated_offset) * (other.velocity.magnitude()/(self.velocity.magnitude() + other.velocity.magnitude()))


        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


        relative_velocity = self.velocity - other.velocity;
        if(relative_velocity.magnitude() == 0):
            return

        intensity = int(relative_velocity.magnitude()/200) + 1
        intensity = min(intensity, 3)
        self.game.balls_hit(intensity)

        spark_pose = self.pose - (self.pose - other.pose) * .5
        intensity = min(relative_velocity.magnitude()**1.5/3000, 1)
        self.small_spark_explosion((spark_pose.x, spark_pose.y), intensity=relative_velocity.magnitude()**1.5/3000)
        self.game.current_scene.shake(10 * intensity + 2, other.pose - self.pose)

        other_relative_vector = collision_normal
        momemtum = relative_velocity * self.mass

        dot_product_vectors = collision_normal.x * relative_velocity.x + collision_normal.y * relative_velocity.y;

        energyRatio = math.sin( math.acos (dot_product_vectors/ (collision_normal.magnitude() * relative_velocity.magnitude()) ) )

        #print(energyRatio)

        if energyRatio<0.2:
            energyRatio = 0.2
        if energyRatio>.8:
            energyRatio = .8


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
        if(wall_tile.top_right_corner):
            wall_pose.x += c.TILE_SIZE/2
            wall_pose.y -= c.TILE_SIZE/2
        if (wall_tile.top_left_corner):
            wall_pose.x -= c.TILE_SIZE / 2
            wall_pose.y -= c.TILE_SIZE / 2
        if (wall_tile.bottom_right_corner):
            wall_pose.x -= c.TILE_SIZE / 2
            wall_pose.y += c.TILE_SIZE / 2
        if (wall_tile.bottom_left_corner):
            wall_pose.x -= c.TILE_SIZE / 2
            wall_pose.y -= c.TILE_SIZE / 2

        offset_required = (collision_normal.magnitude() - (self.radius + c.TILE_SIZE/6)) / 1.9
        collision_normal.scale_to(1)

        dot_product_self = collision_normal.x * self.velocity.x + collision_normal.y * self.velocity.y;

        output_velocity_vector = (collision_normal * 2 * dot_product_self - self.velocity) * wall_tile.bounce_factor
        pass

    def collide_with_wall_corner_2(self, relative_pose, wall_tile):

        #print("Wall_corner")

        center_ball_2_center_wall = relative_pose.copy()

        if( (center_ball_2_center_wall.x >= 0 and (wall_tile.top_right_corner or wall_tile.bottom_right_corner)) or \
            (center_ball_2_center_wall.x <= 0 and (wall_tile.top_left_corner or wall_tile.bottom_left_corner)) or \
            (center_ball_2_center_wall.y <= 0 and (wall_tile.top_left_corner or wall_tile.top_right_corner)) or \
            (center_ball_2_center_wall.y >= 0 and (wall_tile.bottom_left_corner or wall_tile.bottom_right_corner))   ):
            return

        # Offset balls
        collision_normal = center_ball_2_center_wall.copy()

        #offset_required = (collision_normal.magnitude() - (self.radius + c.TILE_SIZE))
        collision_normal.scale_to(1)
        velocity_vector = self.velocity.copy()
        velocity_vector.scale_to(1)
        #self.pose += velocity_vector * (offset_required * math.cos(math.atan2(velocity_vector.y-collision_normal.y, velocity_vector.x-collision_normal.x)))
        dot_product_self_norm = -collision_normal.x * velocity_vector.x + -collision_normal.y * velocity_vector.y;

        angle_vel = math.acos(dot_product_self_norm / (collision_normal.magnitude() * velocity_vector.magnitude()) )

        angle_b = math.asin( (math.sin(angle_vel) / (self.radius + c.TILE_SIZE)) * center_ball_2_center_wall.magnitude() )
        angle_c = math.pi - (angle_b + angle_vel)
        interpolated_offset = ((self.radius + c.TILE_SIZE)/ math.sin(angle_vel)) * math.sin(angle_c)
        #print("OFFSET :" + str(interpolated_offset) + "    angle C: " + str(math.degrees(angle_c)) + "    angle vel: " + str(math.degrees(angle_vel)))
        self.pose -= velocity_vector * abs(interpolated_offset)
        #self.pose += collision_normal * offset_required #THIS MIGHT BE REVERSED

        #distance =
        #collsion normal must be updated and be updated before changing pose
        # NEED TO FIND OUT WHICH WALL CORNER AND MOVE POSE APPROPRIATELY

        dot_product_self = collision_normal.x * self.velocity.x + collision_normal.y * self.velocity.y;

        self.velocity = (collision_normal * 2 * dot_product_self - self.velocity) * wall_tile.bounce_factor * -1

        if (self.velocity.magnitude() < c.MIN_WALL_BOUNCE_SPEED):
            self.velocity.scale_to(c.MIN_WALL_BOUNCE_SPEED)

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
        self.game.current_scene.shake(5)

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
        x -= self.radius * self.scale
        y -= self.radius * self.scale
        surf = self.surf.copy()
        surf.blit(self.shading, (0, 0), special_flags=pygame.BLEND_MULT)
        surf = pygame.transform.scale(surf, (int(self.radius * self.scale * 2), int(self.radius * self.scale * 2)))
        surf.set_colorkey(surf.get_at((0, 0)))
        surf.set_alpha(self.alpha)
        screen.blit(surf, (x, y))

        color = c.BLACK
        if self.turn_in_progress:
            color = c.WHITE
        if not self.outline_hidden and self.alpha > 128:
            pygame.draw.circle(screen, color, (x+self.radius*self.scale, y+self.radius*self.scale), self.radius*self.scale, int(2*self.alpha/255))


    def draw_shadow(self, screen, offset=(0, 0)):
        x, y = self.pose.get_position()
        x += offset[0] - self.radius*self.scale
        y += offset[1] - self.radius*self.scale + self.radius//2
        self.shadow.set_alpha(50 * self.alpha/255)
        screen.blit(pygame.transform.scale(self.shadow, (int(self.radius*self.scale*2), int(self.radius*self.scale*2))), (x, y))

    def small_spark_explosion(self, position, intensity=1):
        # intensity is scaled to range 0.1-1
        intensity = min(max(intensity, 0.1), 1)
        for i in range(10):
            spark = Spark(self.game, *position, intensity=intensity)
            self.game.current_scene.particles.append(spark)

    def make_smoke(self, position, num):
        if self.game.in_simulation:
            return
        for i in range(num):
            smoke = SmokeBit(self.game, *position)
            smoke.radius *= self.radius/60
            self.game.current_scene.floor_particles.append(smoke)

    def sink(self, pocket_pose):
        if not self.can_be_sunk:
            return
        self.tractor_beam_target = pocket_pose
        self.can_collide = False
        self.target_alpha = 0
        self.target_scale = 0.5

    def sink_for_real(self):
        self.sunk = True
        self.turn_in_progress = False
        #TODO add a neat particle effect

    def has_sunk(self):
        return self.sunk


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
        self.can_be_sunk = False

    def update(self, dt, events):
        super().update(dt, events)
        self.inner_ball.pose = self.pose.copy()


    def draw(self, surf, offset=(0, 0)):
        self.inner_ball.draw(surf, offset=offset)
        x = self.pose.x + offset[0] - self.shell_surf.get_width()//2
        y = self.pose.y + offset[1] - self.shell_surf.get_height()//2
        surf.blit(self.shell_surf, (x, y))
        color = c.BLACK
        if self.turn_in_progress:
            color = c.WHITE
        if not self.outline_hidden:
            pygame.draw.circle(surf, color, (x+self.radius, y+self.radius), self.radius, 2)

        diff = self.pose - self.initial_position
        tx = 1 * math.sin(diff.x/7)
        ty = 1 * math.cos(diff.y/7)
        surf.blit(self.twinkle_surf, (x + tx, y + ty))

    def draw_shadow(self, screen, offset=(0, 0)):
        offset = (offset[0], offset[1] + self.inner_ball.radius*0.25)
        self.inner_ball.draw_shadow(screen, offset=offset)