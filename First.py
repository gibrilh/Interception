import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from rendering import draw_cube, background, draw_text, draw_ground_grid, draw_shadow, draw_altitude_line
from drone import Plane
from camera import get_camera_position, init_gl
from constants import depth, cube

# camera settings for it to be moved 
cam_yaw = 0.0       # horizontal angle in radians
cam_pitch = 0.3     # vertical angle in radians
cam_distance = 100  # zoom level
fpv_yaw = 0.0
fpv_pitch = 0.3
cam_mode = 'orbit'  # or 'fpv'

def main(): # window settings
    global cam_yaw, cam_pitch, cam_distance, cam_mode, fpv_yaw, fpv_pitch
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
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    cam_mode = 'fpv' if cam_mode == 'orbit' else 'orbit'
        dt_ms = clock.tick(60)
        dt = dt_ms / 1000

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1, 1, 1, 1)
        background(depth)
        draw_ground_grid(depth, spacing=5)
        draw_shadow(plane.position)
        draw_altitude_line(plane.position)

        keys = pygame.key.get_pressed()

        ax = 0
        ay = 0
        az = 0

        if keys[pygame.K_d]:
            az = 1
        if keys[pygame.K_a]:
            az = -1
        if keys[pygame.K_w]:
            ax = 1
        if keys[pygame.K_s]:
            ax = -1
        if keys[pygame.K_SPACE]:
            ay = 1
        if keys[pygame.K_LSHIFT]:
            ay = -1

        plane.set_input(ax, ay, az)
        plane.update(dt)
        plane.draw()

        # handle camera keys
        if cam_mode == 'fpv':
            if keys[pygame.K_LEFT]:
                fpv_yaw += 0.02
            if keys[pygame.K_RIGHT]:
                fpv_yaw -= 0.02
            if keys[pygame.K_UP]:
                fpv_pitch += 0.02
            if keys[pygame.K_DOWN]:
                fpv_pitch -= 0.02
            fpv_pitch = max(-1.4, min(1.4, fpv_pitch))
        else:
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

        cx, cy, cz = get_camera_position(cam_yaw, cam_pitch, cam_distance)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        if cam_mode == 'orbit':
            cx, cy, cz = get_camera_position(cam_yaw, cam_pitch, cam_distance)
            gluLookAt(cx, cy, cz,
                plane.position[0], plane.position[1], plane.position[2],
                0, 1, 0)
        else:
        # FPV - camera sits inside the drone, looking forward along X axis
            px = plane.position[0] + cube/2
            py = plane.position[1] + cube/2
            pz = plane.position[2] + cube/2
    # compute look direction from fpv_yaw and fpv_pitch
            lx = px + math.cos(fpv_pitch) * math.sin(fpv_yaw)
            ly = py + math.sin(fpv_pitch)
            lz = pz + math.cos(fpv_pitch) * math.cos(fpv_yaw)
            gluLookAt(px, py, pz,
                lx, ly, lz,
                0, 1, 0)
        
        draw_text(570, 500, f"pos: {plane.position.round(1)}")
        draw_text(570, 480, f"vel: {plane.velocity.round(1)}")
        draw_text(570, 460, f"inp: {plane.input.round(1)}")

        pygame.display.flip()

main()
