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
