import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from rendering import draw_axes, draw_cube, background
from drone import Plane
from camera import cam_yaw, cam_pitch, cam_distance, get_camera_position, init_gl
from constants import depth, cube



def main(): # window settings
    global cam_yaw, cam_pitch, cam_distance
    pygame.init()
    screen = pygame.display.set_mode((800,600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("missile simulation")
    clock = pygame.time.Clock()

    init_gl(800, 600)

    plane = Plane()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1, 1, 1, 1)
        background(depth)
        draw_axes()

        keys = pygame.key.get_pressed()

        ax = 0
        ay = 0 
        az = 0 

        # these acceleration values are based on the DJI Air 3S max speed values (up 10m/s, down 10m/s, lateral 21 m/s)
        if keys[pygame.K_d]:
            az = 50
        if keys[pygame.K_a]:
            az = -50
        if keys[pygame.K_w]:
            ax = 50
        if keys[pygame.K_s]:
            ax = -50
        if keys[pygame.K_SPACE]:
            ay = 50
        if keys[pygame.K_LSHIFT]:
            ay = -50
        plane.acceleration = np.array([ax, ay, az], dtype=float)

        plane.update(dt)
        plane.draw()

        # handle camera keys
        if keys[pygame.K_LEFT]:
            cam_yaw += 0.02   # small increment, try 0.02
        if keys[pygame.K_RIGHT]:
            cam_yaw -= 0.02
        if keys[pygame.K_UP]:
            cam_pitch += 0.02
        if keys[pygame.K_DOWN]:
            cam_pitch -= 0.02
        if keys[pygame.K_EQUALS]:
            cam_distance -= 2  # zoom in
        if keys[pygame.K_MINUS]:
            cam_distance += 2  # zoom out
        cam_pitch = max(-1.4, min(1.4, cam_pitch))
        cx, cy, cz = get_camera_position()

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        gluLookAt(cx, cy, cz,
                    0, 50, depth/2,
                    0, 1,  0)

        pygame.display.flip()

main()