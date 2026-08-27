import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from rendering import draw_solid_cube, background, draw_text, draw_ground_grid, draw_shadow, draw_altitude_line, draw_game_over_screen, draw_danger_overlay, draw_compass
from drone import Plane
from camera import get_camera_position, rotate_input_by_yaw, init_gl
from constants import depth, cube, radius 
from interceptor import LaunchSite, Interceptor, Goal

TIME_LIMIT = 30.0 # seconds to reach the goal before it's game over

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
    goal = Goal(radius=20)
    interceptor = None
    interceptor_launched = False
    game_over = False   # True when the round has ended, freezes the action
    win = False          # True if the round ended by reaching the goal, False if caught
    time_left = TIME_LIMIT

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    cam_mode = 'fpv' if cam_mode == 'orbit' else 'orbit'
            if event.type == pygame.MOUSEBUTTONDOWN and game_over:
                plane = Plane()
                launch_site = LaunchSite()
                goal = Goal()
                interceptor = None
                interceptor_launched = False
                game_over = False
                win = False
                time_left = TIME_LIMIT

        dt_ms = clock.tick(60)
        dt = dt_ms / 1000

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(1, 1, 1, 1)

        if cam_mode == 'fpv':
            glEnable(GL_FOG)   # tight visibility feels right up close in the cockpit view
        else:
            glDisable(GL_FOG)  # orbit view wants to see the whole arena clearly

        background(depth)
        draw_ground_grid(depth, spacing=5)
        draw_shadow(plane.position)
        draw_altitude_line(plane.position)

        keys = pygame.key.get_pressed()

        forward = 0
        strafe = 0
        ay = 0

        if not game_over:
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

        if cam_mode == 'fpv':
            ix, iz = rotate_input_by_yaw(forward, -strafe, fpv_yaw)
        else:
            ix, iz = rotate_input_by_yaw(forward, -strafe, cam_yaw + math.pi)

        if not game_over:
            distance_to_site = np.linalg.norm(plane.position - launch_site.position)
            if distance_to_site <= radius and not interceptor_launched:
                interceptor_launched = True
                interceptor = Interceptor(launch_site.position, plane.position)

            plane.set_input(ix, ay, iz)
            plane.update(dt)

        plane.draw_trail()
        plane.draw()
        launch_site.draw()
        launch_site.draw_detection_dome(radius)
        goal.draw()

        if interceptor is not None:
            if not game_over:
                interceptor.update(dt, plane.position, plane.velocity)
            interceptor.draw_trail()
            interceptor.draw()

            if not game_over:
                hit_distance = np.linalg.norm(plane.position - interceptor.position)
                if hit_distance < cube:
                    game_over = True
                    win = False

        if not game_over:
            goal_distance = np.linalg.norm(plane.position - goal.position)
            if goal_distance < goal.radius:
                game_over = True
                win = True

        if not game_over:
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                game_over = True
                win = False

        if interceptor is not None and not game_over:
            t = pygame.time.get_ticks() / 1000
            pulse = 0.15 + 0.1 * abs(math.sin(t * 6))
            draw_danger_overlay(pulse)

        # camera controls
        if cam_mode == 'fpv':
            if keys[pygame.K_LEFT]:
                fpv_yaw += 0.05
            if keys[pygame.K_RIGHT]:
                fpv_yaw -= 0.05
            if keys[pygame.K_UP]:
                fpv_pitch += 0.05
            if keys[pygame.K_DOWN]:
                fpv_pitch -= 0.05
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
                      depth/2, depth/2, depth/2, 0, 1, 0)
        else:
            back_offset = 15
            up_offset = 5
            px = plane.position[0] + cube/2 - back_offset * math.sin(fpv_yaw)
            py = plane.position[1] + cube/2 + up_offset
            pz = plane.position[2] + cube/2 - back_offset * math.cos(fpv_yaw)
            lx = px + math.cos(fpv_pitch) * math.sin(fpv_yaw)
            ly = py + math.sin(fpv_pitch)
            lz = pz + math.cos(fpv_pitch) * math.cos(fpv_yaw)
            gluLookAt(px, py, pz, lx, ly, lz, 0, 1, 0)

        draw_text(570, 500, f"pos: {plane.position.round(1)}")
        draw_text(570, 480, f"vel: {plane.velocity.round(1)}")
        draw_text(570, 460, f"inp: {plane.input.round(1)}")

        timer_color = (0, 0, 0)
        if time_left <= 5:
            flash = abs(math.sin(pygame.time.get_ticks() / 1000 * 6))
            timer_color = (255, 0, 0) if flash > 0.5 else (0, 0, 0)
        draw_text(370, 560, f"TIME: {time_left:04.1f}", color=timer_color)
        view_yaw = fpv_yaw if cam_mode == 'fpv' else (cam_yaw + math.pi)
        draw_compass(plane.position, goal.position, view_yaw)

        if game_over:
            draw_game_over_screen(win)

        pygame.display.flip()

main()