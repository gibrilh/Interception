import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube, radius 
from rendering import draw_cube
import numpy as np

x = np.random.randint(0 + radius,depth - radius )
z = np.random.randint(0 + radius,depth - radius )

class LaunchSite: # plane variables that get updated 
    def __init__(self):
        self.position = np.array([x,0,z], dtype=float)

    def draw(self): # drawing the cube 
        glPushMatrix()
        glTranslatef(*self.position)
        glBegin(GL_QUADS)
        glColor3f(1, 0, 0)  # dark green
        glVertex3f(-cube/2, 0.1, -cube/2)
        glVertex3f( cube/2, 0.1, -cube/2)
        glVertex3f( cube/2, 0.1,  cube/2)
        glVertex3f(-cube/2, 0.1,  cube/2)
        glEnd()
        glPopMatrix()

    def draw_detection_dome(self, radius, segments=24):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_DEPTH_TEST)  # so it renders through other objects, feels like a zone not a solid

        glPushMatrix()
        glTranslatef(*self.position)
        glColor4f(1, 0, 0, 0.15)  # red, low alpha

        for i in range(segments):
            lat0 = math.pi/2 * i / segments        # 0 to pi/2 (top half only = hemisphere)
            lat1 = math.pi/2 * (i+1) / segments

            glBegin(GL_TRIANGLE_STRIP)
            for j in range(segments + 1):
                lon = 2 * math.pi * j / segments

                x0 = radius * math.cos(lat0) * math.cos(lon)
                y0 = radius * math.sin(lat0)
                z0 = radius * math.cos(lat0) * math.sin(lon)

                x1 = radius * math.cos(lat1) * math.cos(lon)
                y1 = radius * math.sin(lat1)
                z1 = radius * math.cos(lat1) * math.sin(lon)

                glVertex3f(x0, y0, z0)
                glVertex3f(x1, y1, z1)
            glEnd()

        glPopMatrix()
        glEnable(GL_DEPTH_TEST)
        glDisable(GL_BLEND)