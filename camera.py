from primitives import GameObject, Pose
import constants as c


class Camera(GameObject):
    def __init__(self, game, object_to_track):
        self.game = game
        self.object_to_track = object_to_track  # should have a 'pose' attribute with a .x and .y
        self.mid_pose = Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2), 0)
        self.pose = object_to_track.pose - self.mid_pose

    def update(self, dt, events):
        diff = self.object_to_track.pose - self.pose - self.mid_pose
        self.pose += diff * dt * 5

    def draw(self, surf, offset=(0, 0)):
        pass

    def add_offset(self, offset):
        return offset[0] - self.pose.x, offset[1] - self.pose.y