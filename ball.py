import pygame
import math
from copy import copy


from primitives import PhysicsObject, Pose
import constants as c
from particle import Spark, SmokeBit, PoofBit, BubbleBurst
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
        self.has_poofed = False
        self.cue = BasicCue()
        self.has_collided = False
        self.collided_with = None
        self.is_simulating = False
        self.attack_on_room_spawn = False
        self.power_boost_factor = 1
        self.intelligence_mult = 1
        self.inaccuracy = 0
        self.max_power_reduction = 0
        self.gravity = 0
        self.can_have_shield = True
        self.attack_on_room_spawn = False
        self.is_boss = False
        self.is_fragile = False
        self.only_hit_player = False
        self.moves_per_turn= 1



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

        ######################################

        relative_position_player_to_pocket = self.pose - player.pose
        _scanner = relative_position_player_to_pocket.copy()
        _scanner *= -1
        _scanner.scale_to(1)

        bank_shot = True
        current_step = 0
        is_wall_2 = False
        while current_step < relative_position_player_to_pocket.magnitude() - c.TILE_SIZE and not is_wall_2:
            to_test_pose = self.pose + (_scanner * current_step)
            to_test_pose = self.round_to_map_coordinate(to_test_pose)

            # test_tile = self.game.current_scene.map.coordinate_collidable(to_test_pose.x, to_test_pose.y)
            # is_wall = test_tile.collidable

            is_wall_2 = current_room.coordinate_collidable(to_test_pose.x, to_test_pose.y)
            # if(is_wall_2):
            #      print("FOUND WALL   CURRENT STEP = " + str(current_step/(c.TILE_SIZE / 2)))
            # else:
            #     print("blatg")

            current_step += c.TILE_SIZE / 2
        bank_shot = is_wall_2

        ##########################################CHECK IF TO PLAYER PATH IS BLOCKED BY WALLS


        #ORDERS POCKETS BY LESS ANGLE NEEDED
        #pockets.sort(key=lambda pocket: abs(math.degrees(math.atan2(player.pose.x - pocket.pose.x, player.pose.y - pocket.pose.y)) - to_player_degrees)   )

        if(not bank_shot):
            pockets = current_room.pockets
            pockets.sort(key=lambda pocket: abs(math.degrees(math.atan2(player.pose.y - pocket.pose.y, -player.pose.x + pocket.pose.x)) - to_player_degrees)   )
            pockets = list(filter(lambda pocket: abs(math.degrees(math.atan2(player.pose.y - pocket.pose.y, -player.pose.x + pocket.pose.x)) - to_player_degrees) < c.AI_MAX_DEFLECTION_ANGLE_ATTEMPTED, pockets))
        #rounded_to_map_player_pose  = self.round_to_map_coordinate(player.pose)

        #CHECK IF POCKET IS VALID (WALLS) HERE


        is_wall = True
        found_pocket = False
        desired_pocket = -1
        wall_check_success = True;

        if(bank_shot):
            print("BANK SHOT")
        while is_wall and not bank_shot:
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
                if(is_wall):
                    print("FOUND WALL (PLAYER TO POCKET)   CURRENT STEP = " + str(current_step / (c.TILE_SIZE/2)))

                current_step += c.TILE_SIZE/2
            found_pocket = not is_wall

        #print("DESIRED POCKET NUMBER " + str(desired_pocket))

        if(found_pocket):
            goal_pocket_angle =  math.degrees(math.atan2(relative_position_player_to_pocket.y, -relative_position_player_to_pocket.x))

            goal_pocket_angle = goal_pocket_angle - to_player_degrees;

            internal_triangle_height = math.sin(math.radians(goal_pocket_angle)) * (self.radius + player.radius)
            goal_offset_angle = math.degrees(math.atan2(internal_triangle_height, relative_position.magnitude() - math.cos(math.radians(goal_pocket_angle)) * (self.radius + player.radius)) )

            if(goal_offset_angle> c.AI_MAX_ANGLE_REDUCTION):
                goal_offset_angle = c.AI_MAX_ANGLE_REDUCTION
            elif(goal_offset_angle< -c.AI_MAX_ANGLE_REDUCTION):
                goal_offset_angle = -c.AI_MAX_ANGLE_REDUCTION

            #print(goal_offset_angle)

            rando_factor = (.4*random.random() + .8)
            _angle_for_pow = abs(math.degrees(math.atan2(player.pose.y - pockets[desired_pocket].pose.y, -player.pose.x + pockets[desired_pocket].pose.x)) - to_player_degrees)
            power = (rando_factor) * ( ((relative_position_player_to_pocket.magnitude() + relative_position.magnitude()) * .2) ) * (90/(90-_angle_for_pow))**.5
            #print((relative_position_player_to_pocket.magnitude() + relative_position.magnitude())*.2)
            #print(power/rando_factor)
            if(power> 100  - self.max_power_reduction):
                power = 100 - self.max_power_reduction
            if(power< rando_factor * 20):
                power = rando_factor * 20
            self.knock(self.cue, to_player_degrees - goal_offset_angle, power)
        else:
            prediction_line_count = 100
            rando_factor = (.4*random.random() + .8)
            print("BRUTE FORCE TIME")
            shot_options = []
            for i in range(0,prediction_line_count-1):
                _hold_pose = self.pose
                _hold_velocity = self.velocity
                self.is_simulating = True
                result = self.do_prediction_line( (360/prediction_line_count)*i + (360/prediction_line_count) * random.random(), rando_factor*(95-self.max_power_reduction))
                self.tractor_beam_target = None
                self.can_collide = True
                self.is_simulating = False
                self.pose = _hold_pose
                self.velocity = _hold_velocity
                #.has_collided = True
                if result==0:
                    result= 0.01

                #print(type(result))
                if(type(result) is float):
                    shot_options.append( ((360/prediction_line_count)*i + (360/prediction_line_count) * random.random(), rando_factor*(95-self.max_power_reduction), result) )
                else:
                    shot_options.append( ((360/prediction_line_count)*i + (360/prediction_line_count) * random.random(), rando_factor*(95-self.max_power_reduction), (result - player.pose)) )

                # if type(shot_options[i][2]) is float:
                #     print("FLOAT OUTPUT: "+ str(shot_options[i][2]))
                #     pass
                # if type(shot_options[i][2]) is Pose:
                #     #shot_options[i][2] -= player.pose
                #     #print("MAG " + str(shot_options[i][2].magnitude()))
                #     pass

            shot_options.sort(key = lambda x: x[2] - 10000 if type(x[2]) is float else x[2].magnitude())
            print("CHOSEN TYPE: " + str(type(shot_options[0][2])) + "   angle: " + str( shot_options[0][0]) + "  power: " + str(shot_options[0][1]))
            # if type(shot_options[0][2]) is float:
            #     print("HIT IT! BRUTE FORCED!")
            self.knock(self.cue, shot_options[0][0], shot_options[0][1])

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
        tiles = list(self.game.current_scene.map.tiles_near(self.pose, self.radius))
        if not len(list(tiles)):
            return False
        tiles = self.game.current_scene.map.tiles_near(self.pose, self.radius)
        for tile in tiles:
            if tile.top_right_corner or tile.top_left_corner or tile.bottom_right_corner or tile.bottom_left_corner:
                continue
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
            #if(self.moves_per_turn <= self.game.current_scene.moves_used):
            self.turn_in_progress = False
            self.turn_phase = c.BEFORE_HIT

        if self.tractor_beam_target:
            diff = self.tractor_beam_target - self.pose
            self.pose += diff*dt * 5

            if (self.tractor_beam_target - self.pose).magnitude() < 2 and not self.is_simulating:
                if self.target_alpha < self.alpha:
                    self.alpha -= 250*dt
                if self.target_scale < self.scale:
                    self.scale -= dt*1.4 - (self.target_scale - self.scale)*4*dt
                    if abs(self.scale - self.target_scale) < 0.05:
                        self.poof()
                if self.alpha < 1:
                    self.sink_for_real()
                    return
            return

        self.update_in_simulation(dt, events) #NOT FOR IN SIM - GRAVITY CODE IN HERE
        super().update(dt, events)  # update position based on velocity, velocity based on acceleration

        #self.drag_continous(dt)
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

    def update_in_simulation(self, dt, events):

        if(self.gravity != 0):
            return

        for ball in self.game.current_scene.balls:
            if(ball.gravity == 0):
                continue
            #print("GRAV TIME")
            delta_pose = self.pose - ball.pose
            grav_factor = (1/(delta_pose.magnitude()**2) - (1/(c.GRAVITY_RADIUS**2)))
            #print("GRAV FACTOR : " +str(grav_factor))
            #print("DELAT MAG: " + str(delta_pose.magnitude() ))

            if(grav_factor<0):
                grav_factor = 0
            #elif(grav_factor> (1/(c.MAX_GRAVITY_AT_RADIUS**2) - (1/(c.GRAVITY_RADIUS**2)))):
            #    grav_factor = (1/(c.MAX_GRAVITY_AT_RADIUS**2) - (1/(c.GRAVITY_RADIUS**2)))
            #print("GRAV FACTOR : " +str(((grav_factor*ball.mass)/self.mass) * ball.gravity * dt))

            delta_pose.scale_to(1)
            self.velocity += delta_pose * ((grav_factor*ball.mass)/self.mass) * ball.gravity * dt


            # if self.turn_in_progress and self.turn_phase == c.BEFORE_HIT and self.is_simulating and (ball.pose - self.pose).magnitude() < c.GRAVITY_RADIUS:
            #      ball.velocity -= delta_pose * ((max(grav_factor,.0001) * ball.mass) / self.mass) * ball.gravity * dt

            #max(grav_factor, .01)

    def drag(self, dt):
        if(self.velocity.magnitude() > self.max_speed):
            self.velocity.scale_to(self.max_speed)
        self.velocity -= self.velocity * self.drag_multiplicative * dt;
        _temp_velocity = self.velocity.copy();
        _temp_velocity.scale_to(1)

        self.velocity -= _temp_velocity * self.drag_constant * dt;

        _drag_factor = _temp_velocity * self.drag_constant * dt;

        if(_drag_factor.magnitude() >= self.velocity.magnitude() ):
            self.velocity = Pose((0,0),0)

    def drag_continous(self, dt):

        b = 5
        g = .1
        c = .03
        drag_scaling_factor = 1

        if(self.velocity.magnitude() != 0):

            #(c*v+b*v^(g))
            velocity_vect = self.velocity.copy()
            velocity_vect.scale_to(1)

            velocity_reduction_point_time = abs(self.velocity.magnitude()*c + (self.velocity.magnitude()**g) * b)
            velocity_reduction_point_time -= dt*drag_scaling_factor
            if(velocity_reduction_point_time<0):
                velocity_reduction_point = 0
            velocity_reduced =  self.velocity.magnitude() - abs(velocity_reduction_point_time*c + (velocity_reduction_point_time**g) * b)
            if(abs(velocity_reduced) < self.velocity.magnitude()):
                print("REDUCCED TO ;" + str(velocity_reduced))
                self.velocity = velocity_vect * velocity_reduced
            else:
                self.velocity.scale_to(0)

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
            if ball.is_player and self.is_player:
                continue
            if (self.only_hit_player and not ball.is_player) or (self.is_player and ball.only_hit_player):
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
                if(ball.is_fragile):
                    ball.break_ball()
                #ball.collide_with_other_ball_2(self)
                break
        #print("update  # mapTiles: ")
        for mapTile in mapTiles: #CORNERS FIRST
            # if(mapTile.key != "."):
            #     print("MAP: " + str(mapTile.key))

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
            self.game.current_scene.shake(8 * self.velocity.magnitude()*self.mass / 500, pose=self.velocity)

        if(self.is_fragile and (self._did_collide_wall or self._did_collide) and not self.is_simulating):
            self.break_ball()

        # TODO iterate through other balls and call self.collide_with_other_ball if colliding
        # TODO iterate through nearby map tiles and call self.collide_with_tile if colliding
        pass
    def break_ball(self):
        #JARM ANIMATION HERE
        balls = self.game.current_scene.balls
        #print("FRAGILE")
        if self.game.current_scene.current_ball == self:# and self.game.current_scene.balls[(self.game.current_scene.balls.index(self.game.current_scene.current_ball) + 1) % len(self.game.current_scene.balls)]:
            self.turn_phase = c.AFTER_HIT
            print("INNER FRAGILE")
            self.game.current_scene.current_ball.turn_in_progress = False
            self.game.current_scene.current_ball = self.game.current_scene.balls[(self.game.current_scene.balls.index(self.game.current_scene.current_ball) + 1) % len(self.game.current_scene.balls)]
        if(self in self.game.current_scene.balls):
            balls.remove(self)
    def do_collision(self, mapTile, interpolate_checked = False):

        if (self.is_fragile and not self.is_simulating):
            self.break_ball()
        #return()
        #print("wall");
        relative_position = self.pose - self.map_coordinate_to_pose(mapTile)

        if(not interpolate_checked):
            #NEARBY CHECK HERE, NEED TO MAKE SURE DIDN"T GLITCH THOUGH EDGE AND HIT THIS, POTENTIALLY PASS BACK TO CORNER COLLIDE
            velocity_vector = self.velocity.copy()
            velocity_vector.scale_to(1)
            slope = velocity_vector.y /velocity_vector.x
            offset_interpolate = Pose((0,0),0)

            if(mapTile.down_bumper):
                if(slope == 0):
                    offset_interpolate.x = 0
                else:
                    offset_interpolate.x = (.5*c.TILE_SIZE - (relative_position.y - self.radius))/slope
                offset_interpolate.y =  .5*c.TILE_SIZE - relative_position.y

            elif (mapTile.up_bumper):
                if (slope == 0):
                    offset_interpolate.x = 0
                else:
                    offset_interpolate.x = (-.5 * c.TILE_SIZE - (relative_position.y + self.radius)) / slope
                offset_interpolate.y = -.5 * c.TILE_SIZE + relative_position.y

            elif (mapTile.right_bumper):
                offset_interpolate.y = (.5 * c.TILE_SIZE - (relative_position.x - self.radius)) * slope
                offset_interpolate.x = .5 * c.TILE_SIZE - relative_position.x

            elif (mapTile.left_bumper):
                offset_interpolate.y = (-.5 * c.TILE_SIZE - (relative_position.x + self.radius)) * slope
                offset_interpolate.x = -.5 * c.TILE_SIZE + relative_position.x

            if(offset_interpolate.x< -c.TILE_SIZE):
                offset_interpolate.x = -c.TILE_SIZE
            elif(offset_interpolate.x> c.TILE_SIZE):
                offset_interpolate.x = c.TILE_SIZE
            if (offset_interpolate.y < -c.TILE_SIZE):
                offset_interpolate.y = -c.TILE_SIZE
            elif (offset_interpolate.y > c.TILE_SIZE):
                offset_interpolate.y = c.TILE_SIZE


            interpolated_position = offset_interpolate+self.pose
            current_room = self.game.current_scene.current_room()
            map_pose = self.round_to_map_coordinate(interpolated_position)
            wall_tile_checker = current_room.get_at_global(map_pose.x, map_pose.y)

            if(wall_tile_checker!=False):
                if(wall_tile_checker.top_right_corner or wall_tile_checker.top_left_corner or wall_tile_checker.bottom_right_corner or wall_tile_checker.bottom_left_corner) and wall_tile_checker.collidable:
                    relative_pose = (self.map_coordinate_to_pose(wall_tile_checker) - self.pose)
                    #print("SENDING TO CORNER CODE!")
                    if wall_tile_checker.collidable and (abs(relative_pose.x) < c.TILE_SIZE / 2 + self.radius and abs(relative_pose.y) < c.TILE_SIZE / 2 + self.radius):
                        if(mapTile.top_left_corner):
                            temp_pose = relative_pose.copy()
                            temp_pose.x += c.TILE_SIZE / 2
                            temp_pose.y += c.TILE_SIZE / 2
                            if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                                self._did_collide_wall = True;
                                self.collide_with_wall_corner_2(temp_pose, mapTile, True)
                        elif (mapTile.top_right_corner):
                            temp_pose = relative_pose.copy()
                            temp_pose.x -= c.TILE_SIZE / 2
                            temp_pose.y += c.TILE_SIZE / 2
                            if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                                self._did_collide_wall = True;
                                self.collide_with_wall_corner_2(temp_pose, mapTile, True)
                        elif (mapTile.bottom_left_corner):
                            temp_pose = relative_pose.copy()
                            temp_pose.x += c.TILE_SIZE / 2
                            temp_pose.y -= c.TILE_SIZE / 2
                            if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                                self._did_collide_wall = True;
                                self.collide_with_wall_corner_2(temp_pose, mapTile, True)
                        elif (mapTile.bottom_right_corner):
                            temp_pose = relative_pose.copy()
                            temp_pose.x -= c.TILE_SIZE / 2
                            temp_pose.y -= c.TILE_SIZE / 2
                            if (temp_pose.magnitude() < c.TILE_SIZE + self.radius):
                                self._did_collide_wall = True;
                                self.collide_with_wall_corner_2(temp_pose, mapTile, True)
                else:
                    self.pose = interpolated_position
            else:
                self.pose = interpolated_position

        self.game.current_scene.shake(8 * self.velocity.magnitude()*self.mass/500, pose=self.velocity)

        #shift pose away from wall

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
        velocity_vector = self.velocity - other.velocity
        velocity_vector.scale_to(1)
        # self.pose += velocity_vector * (offset_required * math.cos(math.atan2(velocity_vector.y-collision_normal.y, velocity_vector.x-collision_normal.x)))
        dot_product_self_norm = collision_normal.x * velocity_vector.x + collision_normal.y * velocity_vector.y;

        if(collision_normal.magnitude() * velocity_vector.magnitude() != 0):
            acos_input = (dot_product_self_norm / (collision_normal.magnitude() * velocity_vector.magnitude()))
        if acos_input > 1:
            acos_input = 1
        elif acos_input < -1:
            acos_input = -1
        angle_vel = math.acos(acos_input)



        angle_b = math.asin((math.sin(angle_vel) / (self.radius + other.radius)) * collision_normal_unscaled.magnitude())
        angle_c = math.pi - (angle_b + angle_vel)
        if(math.sin(angle_vel) == 0):
            angle_vel = 1
        interpolated_offset = ((self.radius + other.radius) / math.sin(angle_vel)) * math.sin(angle_c)
        # print("OFFSET :" + str(interpolated_offset) + "    angle C: " + str(math.degrees(angle_c)) + "    angle vel: " + str(math.degrees(angle_vel)))

        if((self.velocity.magnitude() + other.velocity.magnitude()) != 0):
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
        self.game.current_scene.shake(10 * intensity * self.mass*other.mass + 2, other.pose - self.pose)

        other_relative_vector = collision_normal
        momemtum = relative_velocity * self.mass

        dot_product_vectors = collision_normal.x * relative_velocity.x + collision_normal.y * relative_velocity.y;
        if(collision_normal.magnitude() * relative_velocity.magnitude() != 0):
            acos_input = dot_product_vectors/ (collision_normal.magnitude() * relative_velocity.magnitude())
            if acos_input > 1:
                acos_input = 1
            elif acos_input < -1:
                acos_input = -1
            energyRatio = math.sin( math.acos ( acos_input) )
        else:
            energyRatio = .5

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

        self.on_collide(other)
        other.on_being_hit(self)

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

    def collide_with_wall_corner_2(self, relative_pose, wall_tile, interpolate_checked = False):

        #print("Wall_corner")
        if (self.is_fragile and not self.is_simulating):
            self.break_ball()

        if(not interpolate_checked or True): #CURRENTLY FOCING TO ALLWAYS RUN - THIS MIGHT WORK AND NOT CREATE AN INFINATE LOOP BECAUSE INTERPOLATING AN INERPOLATED POINT SHOULD NOT CALL A WALL AGAIN
            center_ball_2_center_wall = relative_pose.copy()
            collision_normal = center_ball_2_center_wall.copy()


            if( (center_ball_2_center_wall.x >= 0 and (wall_tile.top_right_corner or wall_tile.bottom_right_corner)) or \
                (center_ball_2_center_wall.x <= 0 and (wall_tile.top_left_corner or wall_tile.bottom_left_corner)) or \
                (center_ball_2_center_wall.y <= 0 and (wall_tile.top_left_corner or wall_tile.top_right_corner)) or \
                (center_ball_2_center_wall.y >= 0 and (wall_tile.bottom_left_corner or wall_tile.bottom_right_corner))   ):
                return

            # Offset balls

            #offset_required = (collision_normal.magnitude() - (self.radius + c.TILE_SIZE))
            collision_normal.scale_to(1)
            velocity_vector = self.velocity.copy()
            velocity_vector.scale_to(1)
            #self.pose += velocity_vector * (offset_required * math.cos(math.atan2(velocity_vector.y-collision_normal.y, velocity_vector.x-collision_normal.x)))
            dot_product_self_norm = -collision_normal.x * velocity_vector.x + -collision_normal.y * velocity_vector.y;

            if (collision_normal.magnitude() * velocity_vector.magnitude()) == 0:
                angle_vel = 0
            else:
                acos_input = dot_product_self_norm / (collision_normal.magnitude() * velocity_vector.magnitude())
                if(acos_input<-1):
                    acos_input = -1
                elif(acos_input>1):
                    acos_input = 1
                angle_vel = math.acos(acos_input)

            angle_b = math.asin( (math.sin(angle_vel) / (self.radius + c.TILE_SIZE)) * center_ball_2_center_wall.magnitude() )
            angle_c = math.pi - (angle_b + angle_vel)
            if(math.sin(angle_vel) == 0):
                angle_vel+= math.degrees(1)
            interpolated_offset = ((self.radius + c.TILE_SIZE)/ math.sin(angle_vel)) * math.sin(angle_c)
            #print("OFFSET :" + str(interpolated_offset) + "    angle C: " + str(math.degrees(angle_c)) + "    angle vel: " + str(math.degrees(angle_vel)))
            rewound_self_pose = self.pose - (velocity_vector * abs(interpolated_offset))
            #self.pose += collision_normal * offset_required #THIS MIGHT BE REVERSED
            self.pose = rewound_self_pose;
            ##
            map_pose = self.round_to_map_coordinate(rewound_self_pose)
            current_room = self.game.current_scene.current_room()
            #print("NEW MAP COORDINATE: " +str(map_pose.x) + "    " + str(map_pose.y))
            newTile = current_room.get_at_global(map_pose.x, map_pose.y)
            if(newTile != False):
                if (newTile.up_bumper or newTile.down_bumper or newTile.left_bumper or newTile.right_bumper) and newTile.collidable:
                #DO WALL SEARCH HERE
                    self.do_collision(newTile, True)
                    return()
                else:
                    relative_pose += (velocity_vector * abs(interpolated_offset))
            else:
                relative_pose += (velocity_vector * abs(interpolated_offset))
        else:
            pass

        center_ball_2_center_wall = relative_pose.copy()
        collision_normal = center_ball_2_center_wall.copy()
        collision_normal.scale_to(1)

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
        other_new.scale_to(magnitude * energy_transfer * 0.8)
        vel_change = other_new.copy()
        vel_change.scale_to(magnitude * (1 - energy_transfer) * 0.8)
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
        angle += ((random.random()-.5)*2) * self.inaccuracy
        power *= self.power_boost_factor
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
            pygame.draw.circle(screen, color, (x+self.radius*self.scale, y+self.radius*self.scale), int(self.radius*self.scale) + 1, int(2*self.alpha/255))


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

    def make_poof(self, position, num):
        if self.game.in_simulation:
            return
        for i in range(num):
            smoke = PoofBit(self.game, *position)
            self.game.current_scene.floor_particles.append(smoke)

    def poof(self, on_land=False):
        if self.game.in_simulation:
            return
        if not self.has_poofed:
            if on_land:
                self.make_poof((self.pose + Pose((0, self.radius/2), 0)).get_position(), 16)
            else:
                self.make_poof(self.pose.get_position(), 16)
                self.has_poofed = True

    def sink(self, pocket_pose):
        if not self.can_be_sunk:
            return
        self.tractor_beam_target = pocket_pose
        self.can_collide = False
        self.target_alpha = 0
        self.target_scale = 0.5
        if not self.is_player:
            self.game.current_scene.force_player_next = True

    def sink_for_real(self):
        self.sunk = True
        self.turn_in_progress = False

    def has_sunk(self):
        return self.sunk

    def do_prediction_line(self, angle, power):
        # if not self.turn_in_progress or not self.turn_phase == c.BEFORE_HIT:
        #     return

        self.game.in_simulation = True
        self.has_collided = False
        self.collided_with = None
        #player_copy = copy(self)
        player_copy = self

        player_copy.pose = self.pose.copy()
        player_copy.velocity = self.velocity.copy()
        player_copy.collide_with_other_ball_2 = player_copy.mock_collision
        #mouse_pose = Pose(pygame.mouse.get_pos(), 0) + self.game.current_scene.camera.pose
        #my_pose = self.pose.copy()
        player_copy.knock(self.cue, angle, power)

        traveled = 0
        positions = []
        old = player_copy.pose.copy()
        final_position = None
        #print("SIM START    VEL MAG: " + str(player_copy.velocity.magnitude()) )
        for i in range(round(c.AI_SIM_ITERATIONS * self.intelligence_mult)):
            #print("SIM VEL MAG: " + str(player_copy.velocity.magnitude()))
            if(c.VARIABLE_SIM_SPEED):
                near_wall = False
                if(c.AI_SIM_NEAR_WALL_STEP_REDUCTION != 1):
                    mapTiles = self.game.current_scene.map.tiles_near(player_copy.pose, player_copy.radius + c.AI_SIM_MOVEMENT);
                    for mapTile in mapTiles:
                        if(mapTile.collidable):
                            near_wall = True
                            break
                if near_wall and player_copy.velocity.magnitude() >3:
                    sim_update = ((c.AI_SIM_MOVEMENT) / player_copy.velocity.magnitude() / c.AI_SIM_NEAR_WALL_STEP_REDUCTION)
                elif player_copy.velocity.magnitude() > 1:
                    sim_update = ((c.AI_SIM_MOVEMENT)/player_copy.velocity.magnitude())
                else:
                    final_position = player_copy.pose.copy()
                    break
                    sim_update = 1 / (c.AI_SIM_MIN_FPS)
                if(sim_update> 1 / (c.AI_SIM_MIN_FPS)):
                    sim_update = 1 / (c.AI_SIM_MIN_FPS)
                #mapTiles = self.game.current_scene.map.tiles_near(self.pose, self.radius + );
            else:
                sim_update = 1 / (c.AI_SIM_FPS)

            #for self.game.current_scene.balls

            self.update(sim_update, [])
            #positions.append(player_copy.pose.copy())
            if player_copy.has_collided:
                #print("SIM COLLIDED")
                final_position = player_copy.pose.copy()
                break
            if player_copy.velocity.magnitude() < 1:
                #print("SIM VEL 0")
                final_position = player_copy.pose.copy()
                break
            if player_copy.sunk:
                #print("SIM SUNK")
                final_position = Pose((999999,999999), 0)
                break

            new = player_copy.pose.copy()
            traveled += (new - old).magnitude()
            old = new
            if traveled > c.AI_SIM_MAX_DIST:
                final_position = player_copy.pose.copy()
                print("SIM DISTANCE TIMEOUT    VELOCITY MAG: " + str(player_copy.velocity.magnitude()))
                break

        if(final_position == None):
            #print("SIM ITERATIONS MAXED")
            final_position = player_copy.pose.copy()

        #print((self.pose - final_position.pose).magnitude())

        #print("TRAVELD :" + str(traveled))

        #surf = pygame.Surface((3, 3))
        #surf.fill(c.BLACK)
        #pygame.draw.circle(surf, c.WHITE, (surf.get_width()//2, surf.get_width()//2), surf.get_width()//2)
        #alpha = 255
        #surf.set_colorkey(c.BLACK)
        #for pose in positions[::1]:
            #surf.set_alpha(alpha)
            #screen.blit(surf, (pose.x + offset[0] - surf.get_width()//2, pose.y + offset[1] - surf.get_width()//2))

        #offset_pose = Pose(offset, 0)

        if player_copy.collided_with:
            other = player_copy.collided_with
            to_other = other.pose - player_copy.pose
            #angle = math.degrees(-math.atan2(to_other.y, to_other.x))
            #print("SIM RETURN TRAVELED (A HIT HAPPENED): "+str(traveled))
            self.game.in_simulation = False


            #return(abs(angle - math.degrees(math.atan2(player_copy.velocity.y, player_copy.velocity.x))))
            return(traveled)

        self.game.in_simulation = False
        #print("SIM RETURN LAST")
        return(final_position)

    def mock_collision(self, other): #ONLY FOR MOCK BALL COLLISIONS
        #print("hit something? " + str(other.back_surface.get_at((0,0))) + " " + str(self.back_surface.get_at((0,0))))

        #print("COLLISON")
        if self.has_collided or not other.is_player:
            return
        #print("YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAY")
        self.has_collided = True
        self.collided_with = other

        collision_normal = self.pose - other.pose
        collision_normal_unscaled = collision_normal.copy()

        collision_normal.scale_to(1)
        velocity_vector = self.velocity.copy()
        velocity_vector.scale_to(1)
        # self.pose += velocity_vector * (offset_required * math.cos(math.atan2(velocity_vector.y-collision_normal.y, velocity_vector.x-collision_normal.x)))
        dot_product_self_norm = collision_normal.x * velocity_vector.x + collision_normal.y * velocity_vector.y;

        if((collision_normal.magnitude() * velocity_vector.magnitude()) != 0):
            acos_input = dot_product_self_norm / (collision_normal.magnitude() * velocity_vector.magnitude())
            if(acos_input>1):
                acos_input = 1
            if(acos_input<-1):
                acos_input = -1
            angle_vel = math.acos(acos_input)
        else:
            angle_vel = 1

        angle_b = math.asin((math.sin(angle_vel) / (self.radius + other.radius)) * collision_normal_unscaled.magnitude())
        angle_c = math.pi - (angle_b + angle_vel)

        if(math.sin(angle_vel)== 0):
            angle_vel = 1
        interpolated_offset = ((self.radius + other.radius) / math.sin(angle_vel)) * math.sin(angle_c)
        # print("OFFSET :" + str(interpolated_offset) + "    angle C: " + str(math.degrees(angle_c)) + "    angle vel: " + str(math.degrees(angle_vel)))

        if(self.velocity.magnitude() + other.velocity.magnitude()) != 0:
            self.pose -= velocity_vector * abs(interpolated_offset) * (self.velocity.magnitude()/(self.velocity.magnitude() + other.velocity.magnitude()))
            #other.pose += velocity_vector * abs(interpolated_offset) * (other.velocity.magnitude()/(self.velocity.magnitude() + other.velocity.magnitude()))
    def on_collide(self, other):
        """ Called immediately after a collision """
        pass

    def on_being_hit(self, other):
        """ Called immediately after this ball was hit"""
        pass

    def gain_shell(self):
        #JARM ANIMATION HERE
        mr_shell_face = Shelled(self.game, self)
        self.game.current_scene.balls[self.game.current_scene.balls.index(self)] = mr_shell_face
        if(self.game.current_scene.current_ball == self):
            self.game.current_scene.current_ball = mr_shell_face



class Shelled(Ball):
    def __init__(self, game, inner_ball, **kwargs):
        super().__init__(game, **kwargs)

        self.pose = inner_ball.pose.copy()

        self.inner_ball = inner_ball
        self.radius = self.inner_ball.radius * 1.5
        if self.radius < c.DEFAULT_BALL_RADIUS * 1.5:
            self.radius = c.DEFAULT_BALL_RADIUS * 1.5
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
        self.sheen = pygame.Surface((self.radius*2, self.radius*2))
        self.sheen.fill(c.MAGENTA)
        pygame.draw.circle(self.sheen, c.WHITE, (self.radius, self.radius), self.radius)
        self.sheen.set_colorkey(c.MAGENTA)
        self.sheen.set_alpha(0)
        self.sheen_alpha = 0
        self.twinkle_surf.set_alpha(100)
        self.twinkle_surf.set_colorkey(c.BLACK)
        self.broken = False
        self.can_be_sunk = False
        self.last_velocity = self.velocity.copy()
        self.take_turn = lambda *args: type(self.inner_ball).take_turn(self, *args)
        self.mass = self.inner_ball.mass
        self.gravity = self.inner_ball.gravity
        self.moves_per_turn = self.inner_ball.moves_per_turn

        self.mass = self.inner_ball.mass
        self.power_boost_factor = self.inner_ball.power_boost_factor
        self.max_power_reduction = self.inner_ball.max_power_reduction
        self.intelligence_mult = self.inner_ball.intelligence_mult
        self.inaccuracy = self.inner_ball.inaccuracy
        if(hasattr(self.inner_ball,"till_next_attack")):
            self.till_next_attack = self.inner_ball.till_next_attack
        self.attack_on_room_spawn = self.inner_ball.attack_on_room_spawn

    def gain_shell(self):
        pass

    def give_shell_to(self, other, delay=0):
        self.inner_ball.give_shell_to(other, delay=delay)

    def update(self, dt, events):
        self.last_velocity = self.velocity.copy()
        super().update(dt, events)
        if(not self.game.in_simulation):
            self.inner_ball.pose = self.pose.copy()
            self.sheen_alpha -= 1500*dt
            self.sheen_alpha = max(0, self.sheen_alpha)


    def draw(self, surf, offset=(0, 0)):

        self.inner_ball.draw(surf, offset=offset)
        x = self.pose.x + offset[0] - self.shell_surf.get_width()//2
        y = self.pose.y + offset[1] - self.shell_surf.get_height()//2
        surf.blit(self.shell_surf, (x, y))
        color = c.BLACK
        if self.turn_in_progress:
            color = c.WHITE
        if not self.outline_hidden:
            pygame.draw.circle(surf, color, (x+self.radius, y+self.radius), self.radius + 1, 2)

        diff = self.pose - self.initial_position
        tx = 1 * math.sin(diff.x/7)
        ty = 1 * math.cos(diff.y/7)
        surf.blit(self.twinkle_surf, (x + tx, y + ty))
        self.sheen.set_alpha(self.sheen_alpha)
        surf.blit(self.sheen, (x, y))

    def draw_shadow(self, screen, offset=(0, 0)):
        offset = (offset[0], offset[1] + self.inner_ball.radius*0.25)
        self.inner_ball.draw_shadow(screen, offset=offset)

    def on_being_hit(self, other):
        if not self.turn_in_progress:
            self.sheen_alpha = 150
            if (self.velocity - self.last_velocity).magnitude() > c.SHIELD_STRENGTH  / self.mass:
                self.shatter()

    def shatter(self):
        for i, ball in enumerate(self.game.current_scene.balls):
            if ball is self:
                self.game.current_scene.balls[i] = self.inner_ball
                self.inner_ball.outline_hidden = False
                self.inner_ball.turn_phase = self.turn_phase
                self.inner_ball.turn_in_progress = self.turn_in_progress
                self.inner_ball.velocity = self.velocity.copy()
                self.inner_ball.velocity *= c.SHATTER_SPEED_MULT
                self.large_spark_explosion(self.pose.get_position())
                self.game.current_scene.shake(25)
                break

    def large_spark_explosion(self, position, intensity=1.5):
        self.game.current_scene.particles.append(BubbleBurst(self.game, *position))
        for i in range(20):
            spark = Spark(self.game, *position, intensity=intensity)
            self.game.current_scene.particles.append(spark)
