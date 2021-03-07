class Cue:
    def __init__(self):
        pass

    def power_to_speed(self, power, ball=None):
        # Translate a power (0-100) to the ball's velocity.
        # Ball object passed in in case this depends on ball weight.
        return power*10

    def on_hit(self, ball):
        # Apply some effect to ball on hit
        pass

class BasicCue(Cue):
    pass