import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube 
import numpy as np

def get_camera_position(cam_yaw, cam_pitch, cam_distance):
    x = cam_distance * math.cos(cam_pitch) * math.sin(cam_yaw)
    y = cam_distance * math.sin(cam_pitch)
    z = cam_distance * math.cos(cam_pitch) * math.cos(cam_yaw)
    return x, y, z

def init_gl(width, height):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 2000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()