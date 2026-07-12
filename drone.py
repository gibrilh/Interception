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
        self.acceleration = np.array([0,0,0], dtype=float)
    
    def update(self, dt): # movement settings 
        drag = self.velocity * -1 
        gravity = np.array([0, -9.8, 0], dtype=float)
        net_acceleration = self.acceleration + drag + gravity
        new_velocity = self.velocity + net_acceleration * dt 
        new_position = self.position + new_velocity * dt
        
        self.velocity = new_velocity 
        self.position = new_position

        # boundary settings 
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0

        if self.position[0] > depth - cube : # ground settings d
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