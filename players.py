from cmath import cos, sin

import numpy as np


class Me_Player:
    def __init__(self, position, direction, speed=0.1, turn_speed=np.pi / 30):
        self.position = np.array(position, dtype=float)
        self.direction = np.array(direction, dtype=float)  # Direction vector
        self.speed = speed
        self.turn_speed = turn_speed
        self.field_of_view = .6

    def turn(self, angle):
        """Turn the player by a certain angle."""
        rotation_matrix = np.array([[np.cos(angle), -np.sin(angle)], 
                                    [np.sin(angle), np.cos(angle)]])
        self.direction = np.dot(rotation_matrix, self.direction)

    def move_forward(self):
        """Move the player forward."""
        self.position += self.direction * self.speed

    def move_backward(self):
        """Move the player backward."""
        self.position -= self.direction * self.speed

    # Additional methods for strafing left/right can be added if needed.


