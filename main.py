import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from rendering import background, draw_text, draw_ground_grid, draw_shadow, draw_altitude_line, draw_goal_altitude_line, draw_game_over_screen, draw_danger_overlay, draw_compass, draw_hud, draw_goal_distance
from drone import Plane
from camera import rotate_input_by_yaw, init_gl, update_fpv_camera, update_orbit_camera
from constants import depth, cube, radius, ScreenW, ScreenH
from interceptor import LaunchSite, Interceptor, Goal

time_limit = 150.0 # seconds to reach the goal before it's game over
interceptor_speed_coeff = 1.5 # interceptor speed = this * the drone's own max speed
cam_yaw = 0.6 -math.pi/2
cam_pitch = 0.55  # moderate downward angle - a clear general view without approaching top-down
cam_distance = 450
fpv_yaw = 0.0
fpv_pitch = 0.0
cam_mode = 'orbit'

def main():
    global cam_yaw, cam_pitch, cam_distance, cam_mode, fpv_yaw, fpv_pitch
    pygame.init()
    screen = pygame.display.set_mode((ScreenW,ScreenH), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("missile simulation")
    clock = pygame.time.Clock()

    init_gl(ScreenW, ScreenH)

    plane = Plane()
    launch_site = LaunchSite()
    goal = Goal(radius=20)
    interceptor = None
    interceptor_launched = False
    game_over = False   # True when the round has ended, freezes the action
    win = False  # True if the round ended by reaching the goal, False if caught
    time_left = time_limit

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
                goal = Goal(radius=20)
                interceptor = None
                interceptor_launched = False
                game_over = False
                win = False
                time_left = time_limit

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

        view_yaw = fpv_yaw if cam_mode == 'fpv' else (cam_yaw + math.pi)
        ix, iz = rotate_input_by_yaw(forward, -strafe, view_yaw)

        distance_to_site = np.linalg.norm(plane.position - launch_site.position)
        if not game_over:
            if distance_to_site <= radius and not interceptor_launched:
                interceptor_launched = True
                interceptor = Interceptor(launch_site.position, plane.position, speed_coeff=interceptor_speed_coeff)

            plane.set_input(ix, ay, iz)
            plane.update(dt, view_yaw)

        plane.draw_trail()
        plane.draw()
        launch_site.draw()
        launch_site.draw_detection_dome(radius)
        goal.draw_ground_ring()
        goal.draw()
        draw_goal_altitude_line(goal.position)

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

        goal_distance = np.linalg.norm(plane.position - goal.position)
        if not game_over:
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

        # camera section: input handling + view matrix, one branch per mode
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        if cam_mode == 'fpv':
            fpv_yaw, fpv_pitch = update_fpv_camera(keys, fpv_yaw, fpv_pitch, plane.position)
        else:
            cam_yaw, cam_pitch, cam_distance = update_orbit_camera(keys, cam_yaw, cam_pitch, cam_distance)

        draw_hud(np.linalg.norm(plane.velocity), plane.position[1])

        timer_color = (0, 0, 0)
        if time_left <= 5:
            flash = abs(math.sin(pygame.time.get_ticks() / 1000 * 6))
            timer_color = (255, 0, 0) if flash > 0.5 else (0, 0, 0)
        draw_text(370, 560, f"TIME: {time_left:04.1f}", color=timer_color)
        draw_compass(plane.position, goal.position, view_yaw)
        draw_goal_distance(goal_distance)

        if game_over:
            draw_game_over_screen(win)

        pygame.display.flip()

main()