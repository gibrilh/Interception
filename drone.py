import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube 
from rendering import draw_solid_cube
from collections import deque 
import numpy as np

scaler = 5

class Plane: # plane variables that get updated 
    def __init__(self):
        x = np.random.randint(0, depth)
        z = np.random.randint(0, depth)
        y = 0  # spawn on ground 
        self.position = np.array([x, y, z], dtype=float)
        self.velocity = np.array([0,0,0], dtype=float)
        self.input = np.array([0, 0, 0], dtype=float)
        self.trail = deque(maxlen=40)
    
    def set_input(self, ix, iy, iz):
        self.input = np.array([ix, iy, iz], dtype=float)

    def draw_trail(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        n = len(self.trail)
        glBegin(GL_LINE_STRIP)
        for i, p in enumerate(self.trail):
            a = i / max(1, n)
            glColor4f(0.2, 0.9, 1.0, a * 0.8)
            glVertex3f(p[0] + cube/2, p[1] + cube/2, p[2] + cube/2)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)
    
    def update(self, dt): # movement settings 
        # For the X axis 
        if self.input[0] == 0:
            # decelerate towards zero, don't overshoot it
            if self.velocity[0] > 0:
                ax = -5.5 * scaler
            elif self.velocity[0] < 0:
                ax = 5.5 * scaler
            else:
                ax = 0

        elif self.input[0] * self.velocity[0] >= 0: # acceleration
            ax = 4.5 * self.input[0] * scaler

        else: # braking
            ax = 7.0 * self.input[0] * scaler

        # For Y axis 
        if self.input[1] == 0:
            if self.velocity[1] > 0:
                ay = -4 * scaler
            elif self.velocity[1] < 0:
                ay = 4 * scaler
            else:
                ay = 0

        elif self.input[1] * self.velocity[1] >= 0:
            ay = 4 * self.input[1] * scaler

        else:
            ay = 5.0 * self.input[1] * scaler
    
        # For the Z axis 
        if self.input[2] == 0:
            # decelerate towards zero, don't overshoot it
            if self.velocity[2] > 0:
                az = -5.5 * scaler
            elif self.velocity[2] < 0:
                az = 5.5 * scaler
            else:
                az = 0

        elif self.input[2] * self.velocity[2] >= 0: # acceleration
            az = 4.5 * self.input[2] * scaler

        else: # braking
            az = 7.0 * self.input[2] * scaler

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

        self.trail.append(self.position.copy())
    
    def draw(self): # drawing the cube 
        glPushMatrix()
        glTranslatef(*self.position)
        draw_solid_cube((0.2, 0.7, 1.0))
        glPopMatrix()

    