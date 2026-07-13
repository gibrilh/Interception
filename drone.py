import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube 
from rendering import draw_axes, draw_cube, background
import numpy as np

class Plane: # plane variables that get updated 
    def __init__(self):
        self.position = np.array([0,0,0], dtype=float)
        self.velocity = np.array([0,0,0], dtype=float)
        self.input = np.array([0, 0, 0], dtype=float)
    
    def set_input(self, ix, iy, iz):
        self.input = np.array([ix, iy, iz], dtype=float)
    
    def update(self, dt): # movement settings 
        # For the X axis 
        if self.input[0] == 0:
            # decelerate towards zero, don't overshoot it
            if self.velocity[0] > 0:
                ax = -5.5
            elif self.velocity[0] < 0:
                ax = 5.5
            else:
                ax = 0

        elif self.input[0] * self.velocity[0] >= 0: # acceleration
            ax = 4.5 * self.input[0]

        else: # braking
            ax = 7.0 * self.input[0]

        # For Y axis 
        if self.input[1] == 0:
            if self.velocity[1] > 0:
                ay = -4
            elif self.velocity[1] < 0:
                ay = 4
            else:
                ay = 0

        elif self.input[1] * self.velocity[1] >= 0:
            ay = 4 * self.input[1]

        else:
            ay = 5.0 * self.input[1]
    
        # For the Z axis 
        if self.input[2] == 0:
            # decelerate towards zero, don't overshoot it
            if self.velocity[2] > 0:
                az = -5.5
            elif self.velocity[2] < 0:
                az = 5.5
            else:
                az = 0

        elif self.input[2] * self.velocity[2] >= 0: # acceleration
            az = 4.5 * self.input[2]

        else: # braking
            az = 7.0 * self.input[2]

        self.velocity[0] += ax * dt
        self.velocity[1] += ay * dt
        self.velocity[2] += az * dt

        self.velocity[0] = max(-21, min(21, self.velocity[0]))
        self.velocity[1] = max(-10, min(10, self.velocity[1]))
        self.velocity[2] = max(-21, min(21, self.velocity[2]))

        self.position += self.velocity * dt

        # boundary settings 
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0

        if self.position[0] > depth - cube : # ground settings 
            self.position[0] = depth - cube 
            self.velocity[0] = 0

        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0

        if self.position[1] > depth - cube : # ground settings 
            self.position[1] = depth - cube 
            self.velocity[1] = 0

        if self.position[2] < 0:
            self.position[2] = 0
            self.velocity[2] = 0

        if self.position[2] > depth - cube : # ground settings 
            self.position[2] = depth - cube 
            self.velocity[2] = 0
    
    def draw(self): # drawing the cube 
        glPushMatrix()
        glTranslatef(*self.position)
        draw_cube()
        glPopMatrix()