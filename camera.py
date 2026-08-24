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

def rotate_input_by_yaw(forward, strafe, yaw):
    # Converts 'forward' (W/S) and 'strafe' (A/D) intent into world-space X/Z input, based on the current camera yaw angle.
    ix = forward * math.sin(yaw) + strafe * math.cos(yaw)
    iz = forward * math.cos(yaw) - strafe * math.sin(yaw)
    return ix, iz

def init_gl(width, height):
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    glLightfv(GL_LIGHT0, GL_POSITION, (100.0, 300.0, 150.0, 1.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.35, 0.35, 0.4, 1.0))

    glEnable(GL_FOG)   # depth cue — distant stuff fades into sky
    glFogi(GL_FOG_MODE, GL_LINEAR)
    glFogfv(GL_FOG_COLOR, (0.5, 0.75, 1.0, 1.0))
    glFogf(GL_FOG_START, 120)
    glFogf(GL_FOG_END, 400)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 2000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()