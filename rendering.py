import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube 
import numpy as np

def draw_axes(): # edges
    glBegin(GL_LINES)
    glColor3f(0, 0, 0)

    # bottom face
    glVertex3f(0, 0, 0)
    glVertex3f(depth-1, 0, 0)

    glVertex3f(depth-1, 0, 0)
    glVertex3f(depth-1, 0, depth-1)

    glVertex3f(depth-1, 0, depth-1)
    glVertex3f(0, 0, depth-1)

    glVertex3f(0, 0, depth-1)
    glVertex3f(0, 0, 0)

    # top face
    glVertex3f(0, depth-1, 0)
    glVertex3f(depth-1, depth-1, 0)

    glVertex3f(depth-1, depth-1, 0)
    glVertex3f(depth-1, depth-1, depth-1)

    glVertex3f(depth-1, depth-1, depth-1)
    glVertex3f(0, depth-1, depth-1)

    glVertex3f(0, depth-1, depth-1)
    glVertex3f(0, depth-1, 0)

    # vertical edges
    glVertex3f(0, 0, 0)
    glVertex3f(0, depth-1, 0)

    glVertex3f(depth-1, 0, 0)
    glVertex3f(depth-1, depth-1, 0)

    glVertex3f(depth-1, 0, depth-1)
    glVertex3f(depth-1, depth-1, depth-1)

    glVertex3f(0, 0, depth-1)
    glVertex3f(0, depth-1, depth-1)

    glEnd()

def draw_cube():  # drawing cube 
    glBegin(GL_LINES)
    glColor3f(0, 1, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, cube)

    glVertex3f(0, 0, 0)
    glVertex3f(0, cube, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(cube, 0, 0)

    glVertex3f(0, 0, cube)
    glVertex3f(0, cube, cube)

    glVertex3f(0, cube, 0)
    glVertex3f(0, cube, cube)

    glVertex3f(cube, 0, 0)
    glVertex3f(cube, cube, 0)

    glVertex3f(cube, cube, 0)
    glVertex3f(cube, cube, cube)

    glVertex3f(0, cube, cube)
    glVertex3f(cube, cube, cube)

    glVertex3f(0, cube, 0)
    glVertex3f(cube, cube, 0)

    glVertex3f(0, 0, cube)
    glVertex3f(cube, 0, cube)

    glVertex3f(cube, 0, cube)
    glVertex3f(cube, cube, cube)

    glVertex3f(cube, 0, 0)
    glVertex3f(cube, 0, cube)
    
    glEnd()

def background(depth):
    # sky 1 
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(0,      0, 0)
    glVertex3f( depth,      0, 0)
    glVertex3f( depth,  depth, 0)
    glVertex3f(0,  depth, 0)
    glEnd()

    # sky 2 
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(depth, 0,       0)
    glVertex3f(depth, 0,       depth)
    glVertex3f(depth, depth, depth)
    glVertex3f(depth, depth, 0)
    glEnd()

    # ground
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.6, 0.2)
    glVertex3f(0, 0, 0)
    glVertex3f( depth, 0, 0)
    glVertex3f( depth, 0,  depth)
    glVertex3f(0, 0,  depth)
    glEnd()

def draw_text(x, y, text, screen_width=800, screen_height=600):
    font = pygame.font.SysFont('monospace', 18)
    text_surface = font.render(text, True, (0, 0, 0))
    text_data = pygame.image.tostring(text_surface, 'RGBA', True)
    w, h = text_surface.get_size()

    # switch to 2D mode
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glDeleteTextures([tex])

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_ground_grid(depth, spacing=20):
    glBegin(GL_LINES)
    glColor3f(0.3, 0.5, 0.3)  # darker green than background
    for i in range(0, depth + 1, spacing):
        # lines along X
        glVertex3f(0, 0, i)
        glVertex3f(depth, 0, i)
        # lines along Z
        glVertex3f(i, 0, 0)
        glVertex3f(i, 0, depth)
    glEnd()