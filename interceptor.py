import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube, radius, drone_H_speed, drone_V_speed
from rendering import draw_dart, draw_trail
from camera import smooth_yaw_towards
from collections import deque
import numpy as np

class LaunchSite: # launch site parameters 
    def __init__(self):
        x = np.random.randint(0 + radius, depth - radius)
        z = np.random.randint(0 + radius, depth - radius)
        self.position = np.array([x, 0, z], dtype=float)

    def draw(self): # launch site base drawn 
        glPushMatrix()
        glTranslatef(*self.position)
        glBegin(GL_QUADS)
        glColor3f(1, 0, 0)
        glVertex3f(-cube/2, 0.1, -cube/2)
        glVertex3f( cube/2, 0.1, -cube/2)
        glVertex3f( cube/2, 0.1,  cube/2)
        glVertex3f(-cube/2, 0.1,  cube/2)
        glEnd()
        glPopMatrix()

    def draw_detection_dome(self, radius, segments=24):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)
        glPushMatrix()
        glTranslatef(*self.position)
        glColor4f(1, 0, 0, 0.2)  # red, low opacity

        for i in range(segments):
            lat0 = math.pi/2 * i / segments
            lat1 = math.pi/2 * (i+1) / segments

            glBegin(GL_TRIANGLE_STRIP)
            for j in range(segments + 1):
                lon = 2 * math.pi * j / segments
                x0 = radius * math.cos(lat0) * math.cos(lon)
                y0 = radius * math.sin(lat0)
                z0 = radius * math.cos(lat0) * math.sin(lon)
                x1 = radius * math.cos(lat1) * math.cos(lon)
                y1 = radius * math.sin(lat1)
                z1 = radius * math.cos(lat1) * math.sin(lon)
                glVertex3f(x0, y0, z0)
                glVertex3f(x1, y1, z1)
            glEnd()

        glPopMatrix()
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

class Interceptor:
    MIN_RANGE = cube * 3 

    def __init__(self, start_position, target_position, speed_coeff=1.0, N=4, turn_rate_deg=260):
        self.position = start_position.copy()
        self.speed_coeff = speed_coeff  # scales the interceptor's speed relative to the drone's own max speed
        self.speed = speed_coeff * drone_H_speed           # horizontal cruise speed
        self.vertical_speed = speed_coeff * drone_V_speed  # separate vertical cap, same shape as the drone's
        self.N = N    # how strongly it reacts to LOS rotation, below the hard turn-rate cap
        self.max_turn_rate = math.radians(turn_rate_deg)  # hard cap on how fast the heading can bend, in rad/s
        self.trail = deque(maxlen=40)

        # aim straight at the target's starting position instead of starting from rest
        aim = target_position - start_position
        dist = np.linalg.norm(aim)
        heading = (aim / dist) if dist > 1e-6 else np.array([0.0, 0.0, 1.0])
        self.velocity = self._compose_velocity(heading)
        self.facing_yaw = math.atan2(self.velocity[0], self.velocity[2])

    def _compose_velocity(self, heading):
        horiz = np.array([heading[0], 0.0, heading[2]])
        horiz_norm = np.linalg.norm(horiz)
        horiz_dir = horiz / horiz_norm if horiz_norm > 1e-6 else np.array([0.0, 0.0, 1.0])

        vertical = max(-self.vertical_speed, min(self.vertical_speed, heading[1] * self.speed))
        velocity = horiz_dir * self.speed
        velocity[1] = vertical
        return velocity

    def _heading(self):
        v = self.velocity
        n = np.linalg.norm(v)
        return v / n if n > 1e-6 else np.array([0.0, 0.0, 1.0])

    def update(self, dt, target_position, target_velocity):
        R = target_position - self.position
        range_ = np.linalg.norm(R)
        if range_ < 1e-6:
            self.position += self.velocity * dt
            self._clamp_to_bounds()
            return

        los_unit = R / range_
        V_rel = target_velocity - self.velocity
        heading = self._heading()
        range_sq = max(range_ * range_, self.MIN_RANGE ** 2)
        omega = np.cross(R, V_rel) / range_sq
        Vc = -np.dot(V_rel, los_unit)  # closing velocity: how fast the range is shrinking

        if Vc > 0:
            steer = np.cross(omega, los_unit)
        else:
            steer = los_unit - heading

        steer = steer - np.dot(steer, heading) * heading
        steer_mag = np.linalg.norm(steer)

        if steer_mag > 1e-6:
            turn_dir = steer / steer_mag
            dtheta = min(self.N * steer_mag * dt, self.max_turn_rate * dt)
            heading = heading * math.cos(dtheta) + turn_dir * math.sin(dtheta)
            heading = heading / np.linalg.norm(heading)

        self.velocity = self._compose_velocity(heading)
        self.position += self.velocity * dt
        self._clamp_to_bounds()

        horiz_speed = math.hypot(self.velocity[0], self.velocity[2])
        if horiz_speed > 1.0:
            target_yaw = math.atan2(self.velocity[0], self.velocity[2])
            self.facing_yaw = smooth_yaw_towards(self.facing_yaw, target_yaw, self.max_turn_rate * dt)

    def _clamp_to_bounds(self):
        for i in range(3):
            if self.position[i] < 0:
                self.position[i] = 0
                self.velocity[i] = max(self.velocity[i], 0)
            elif self.position[i] > depth - cube:
                self.position[i] = depth - cube
                self.velocity[i] = min(self.velocity[i], 0)
        self.trail.append(self.position.copy())

    def draw(self):
        glPushMatrix()
        glTranslatef(self.position[0] + cube/2, self.position[1] + cube/2, self.position[2] + cube/2)
        glRotatef(math.degrees(self.facing_yaw), 0, 1, 0)
        draw_dart((1.0, 0.2, 0.15))
        glPopMatrix()

    def draw_trail(self):
        draw_trail(self.trail, (0.9, 0.0, 0.0))

class Goal:
    def __init__(self, radius=15):
        x = np.random.randint(0, depth)
        y = np.random.randint(0, depth)
        z = np.random.randint(0, depth)
        self.position = np.array([x, y, z], dtype=float)
        self.radius = radius

    def draw(self, segments=16):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)

        glPushMatrix()
        glTranslatef(*self.position)
        glColor4f(0, 1, 0, 0.35)

        for i in range(segments):
            lat0 = math.pi * (-0.5 + i / segments)
            lat1 = math.pi * (-0.5 + (i+1) / segments)

            glBegin(GL_TRIANGLE_STRIP)
            for j in range(segments + 1):
                lon = 2 * math.pi * j / segments

                x0 = self.radius * math.cos(lat0) * math.cos(lon)
                y0 = self.radius * math.sin(lat0)
                z0 = self.radius * math.cos(lat0) * math.sin(lon)

                x1 = self.radius * math.cos(lat1) * math.cos(lon)
                y1 = self.radius * math.sin(lat1)
                z1 = self.radius * math.cos(lat1) * math.sin(lon)

                glVertex3f(x0, y0, z0)
                glVertex3f(x1, y1, z1)
            glEnd()

        glPopMatrix()
        glDepthMask(GL_TRUE)
        glDisable(GL_BLEND)

    def draw_ground_ring(self, segments=32):
        # marks the goal's (x,z) footprint on the ground - tells you where to
        # stand regardless of how high up the goal itself floats
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)

        x, y, z = self.position

        glColor4f(0, 1, 0, 0.12)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(x, 0.15, z)
        for i in range(segments + 1):
            a = 2 * math.pi * i / segments
            glVertex3f(x + self.radius * math.cos(a), 0.15, z + self.radius * math.sin(a))
        glEnd()

        glColor4f(0, 1, 0, 0.7)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            a = 2 * math.pi * i / segments
            glVertex3f(x + self.radius * math.cos(a), 0.15, z + self.radius * math.sin(a))
        glEnd()

        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        glDisable(GL_BLEND)