import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from rendering import draw_cube, background, draw_text, draw_ground_grid, draw_shadow, draw_altitude_line
from drone import Plane
from camera import get_camera_position, rotate_input_by_yaw, init_gl
from constants import depth, cube, radius 
from interceptor import LaunchSite

# camera settings
cam_yaw = 0.6
cam_pitch = 0.5
cam_distance = 350
fpv_yaw = 0.0
fpv_pitch = 0.0
cam_mode = 'orbit'

def main():
    global cam_yaw, cam_pitch, cam_distance, cam_mode, fpv_yaw, fpv_pitch
    pygame.init()
    screen = pygame.display.set_mode((800,600), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("missile simulation")
    clock = pygame.time.Clock()

    init_gl(800, 600)

    plane = Plane()
    launch_site = LaunchSite()

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

        forward = 0
        strafe = 0
        ay = 0

        if keys[pygame.K_w]:
            forward = 1
        if keys[pygame.K_s]:
            forward = -1
        if keys[pygame.K_d]:
            strafe = 1
        if keys[pygame.K_a]:
            strafe = -1
        if keys[pygame.K_SPACE]:
            ay = 1
        if keys[pygame.K_LSHIFT]:
            ay = -1

        # Rotate movement input based on which camera is active
        if cam_mode == 'fpv':
            ix, iz = rotate_input_by_yaw(forward, strafe, fpv_yaw)
        else:
            ix, iz = rotate_input_by_yaw(forward, -strafe, cam_yaw + math.pi)

        plane.set_input(ix, ay, iz)
        plane.update(dt)
        plane.draw()
        launch_site.draw()
        launch_site.draw_detection_dome(radius)

        # camera controls
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
                cam_yaw += 0.02
            if keys[pygame.K_RIGHT]:
                cam_yaw -= 0.02
            if keys[pygame.K_UP]:
                cam_pitch += 0.02
            if keys[pygame.K_DOWN]:
                cam_pitch -= 0.02
            if keys[pygame.K_EQUALS]:
                cam_distance -= 4
            if keys[pygame.K_MINUS]:
                cam_distance += 4
            cam_pitch = max(-1.4, min(1.4, cam_pitch))
            cam_distance = max(50, min(800, cam_distance))

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if cam_mode == 'orbit':
            cx, cy, cz = get_camera_position(cam_yaw, cam_pitch, cam_distance)
            gluLookAt(cx + depth/2, cy + depth/2, cz + depth/2,
                      depth/2, depth/2, depth/2,
                      0, 1, 0)
        else:
            px = plane.position[0] + cube/2
            py = plane.position[1] + cube/2
            pz = plane.position[2] + cube/2
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