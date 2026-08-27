import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube, radius 
from rendering import draw_solid_cube
from collections import deque
import numpy as np

class LaunchSite: # plane variables that get updated 
    def __init__(self):
        x = np.random.randint(0 + radius, depth - radius)
        z = np.random.randint(0 + radius, depth - radius)
        self.position = np.array([x, 0, z], dtype=float)

    def draw(self): # drawing the cube 
        glPushMatrix()
        glTranslatef(*self.position)
        glBegin(GL_QUADS)
        glColor3f(1, 0, 0)  # dark green
        glVertex3f(-cube/2, 0.1, -cube/2)
        glVertex3f( cube/2, 0.1, -cube/2)
        glVertex3f( cube/2, 0.1,  cube/2)
        glVertex3f(-cube/2, 0.1,  cube/2)
        glEnd()
        glPopMatrix()

    def draw_detection_dome(self, radius, segments=24):
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glDepthMask(GL_FALSE)  # test against depth so cubes occlude it, but don't write so it stays a "zone"

        glPushMatrix()
        glTranslatef(*self.position)
        glColor4f(1, 0, 0, 0.15)  # red, low alpha

        for i in range(segments):
            lat0 = math.pi/2 * i / segments        # 0 to pi/2 (top half only = hemisphere)
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
    MIN_RANGE = cube * 3  # below this, freeze the LOS-rate term instead of letting it blow up

    def __init__(self, start_position, target_position, speed=21, N=3):
        self.position = start_position.copy()
        self.speed = speed # missile flies at constant speed; PN only ever steers its heading
        self.N = N    # navigation constant - higher = more aggressive lead, more oscillation
        self.max_accel = speed * 1.2  # clamp on commanded turn so it curves instead of snapping
        self.trail = deque(maxlen=40)

        # aim straight at the target's starting position instead of starting from rest
        aim = target_position - start_position
        dist = np.linalg.norm(aim)
        self.velocity = (aim / dist * speed) if dist > 1e-6 else np.array([0, 0, speed], dtype=float)

    def update(self, dt, target_position, target_velocity):
        R = target_position - self.position
        range_ = np.linalg.norm(R)
        if range_ < 1e-6:
            self.position += self.velocity * dt
            self._clamp_to_bounds()
            return

        los_unit = R / range_
        V_rel = target_velocity - self.velocity

        # line-of-sight rotation rate as a vector (analytic, no history needed).
        # Floor the range used in the denominator so omega doesn't diverge as
        # range_ -> 0 right before impact (true PN's classic singularity).
        range_sq = max(range_ * range_, self.MIN_RANGE ** 2)
        omega = np.cross(R, V_rel) / range_sq
        # closing velocity: how fast the range is shrinking
        Vc = -np.dot(V_rel, los_unit)

        # true proportional navigation: accelerate perpendicular to the LOS,
        # proportional to closing speed and how fast the LOS is rotating
        a_cmd = self.N * Vc * np.cross(omega, los_unit)

        a_mag = np.linalg.norm(a_cmd)
        if a_mag > self.max_accel:
            a_cmd = a_cmd / a_mag * self.max_accel

        self.velocity += a_cmd * dt
        v_mag = np.linalg.norm(self.velocity)
        if v_mag > 1e-6:
            self.velocity = self.velocity / v_mag * self.speed   # speed stays constant, only heading bends
        else:
            self.velocity = los_unit * self.speed

        self.position += self.velocity * dt
        self._clamp_to_bounds()

    def _clamp_to_bounds(self):
        # keep the missile inside the same play area the drone is confined to
        for i in range(3):
            if self.position[i] < 0:
                self.position[i] = 0
                self.velocity[i] = abs(self.velocity[i])   # bounce heading back inward
            elif self.position[i] > depth - cube:
                self.position[i] = depth - cube
                self.velocity[i] = -abs(self.velocity[i])
        self.trail.append(self.position.copy())

    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        glColor3f(1, 0, 0)
        draw_solid_cube((1.0, 0.2, 0.15))
        glPopMatrix()

    def draw_trail(self):
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        n = len(self.trail)
        glBegin(GL_LINE_STRIP)
        for i, p in enumerate(self.trail):
            a = i / max(1, n)
            glColor4f(0.9, 0, 0, a * 0.8)
            glVertex3f(p[0] + cube/2, p[1] + cube/2, p[2] + cube/2)
        glEnd()
        glDisable(GL_BLEND)
        glEnable(GL_LIGHTING)

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