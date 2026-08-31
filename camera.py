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

def smooth_yaw_towards(current, target, max_step):
    diff = (target - current + math.pi) % (2 * math.pi) - math.pi
    diff = max(-max_step, min(max_step, diff))
    return current + diff

def update_fpv_camera(keys, fpv_yaw, fpv_pitch, plane_position):
    # handles fpv look input, then positions/aims the camera and calls gluLookAt
    if keys[pygame.K_LEFT]:
        fpv_yaw += 0.05
    if keys[pygame.K_RIGHT]:
        fpv_yaw -= 0.05
    if keys[pygame.K_UP]:
        fpv_pitch += 0.05
    if keys[pygame.K_DOWN]:
        fpv_pitch -= 0.05
    fpv_pitch = max(-1.4, min(1.4, fpv_pitch))

    back_offset = 15
    up_offset = 5
    px = plane_position[0] + cube/2 - back_offset * math.sin(fpv_yaw)
    py = plane_position[1] + cube/2 + up_offset
    pz = plane_position[2] + cube/2 - back_offset * math.cos(fpv_yaw)
    lx = px + math.cos(fpv_pitch) * math.sin(fpv_yaw)
    ly = py + math.sin(fpv_pitch)
    lz = pz + math.cos(fpv_pitch) * math.cos(fpv_yaw)
    gluLookAt(px, py, pz, lx, ly, lz, 0, 1, 0)

    return fpv_yaw, fpv_pitch

def update_orbit_camera(keys, cam_yaw, cam_pitch, cam_distance):
    if keys[pygame.K_EQUALS]:
        cam_distance -= 4
    if keys[pygame.K_MINUS]:
        cam_distance += 4
    cam_distance = max(50, min(800, cam_distance))

    cx, cy, cz = get_camera_position(cam_yaw, cam_pitch, cam_distance)
    gluLookAt(cx + depth/2, cy + depth/2, cz + depth/2, depth/2, depth/2, depth/2, 0, 1, 0)

    return cam_yaw, cam_pitch, cam_distance

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