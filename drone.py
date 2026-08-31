# player-controlled drone (Plane class). Physics update order each frame:
# 1 read per-axis input -> acceleration (accelerate, decelerate-to-zero, or brake if reversing)
# 2 clamp velocity to the drone's max horizontal/vertical speed
# 3 integrate velocity into position, clamp position to the play area boundary
# 4 smooth the visual facing direction toward velocity (or camera yaw if nearly idle)

import pygame
import math
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube, drone_H_speed, drone_V_speed
from rendering import draw_dart, draw_trail
from camera import smooth_yaw_towards
from collections import deque
import numpy as np

scaler = 5
X_Z_TUNING = (5.5 * scaler, 4.5 * scaler, 7.0 * scaler)  # x/z: (decelerate, accelerate, brake)
Y_TUNING   = (4.0 * scaler, 4.0 * scaler, 5.0 * scaler)  # y: softer accel/brake than x/z

def _axis_accel(input_i, velocity_i, tuning): # returns this frame's acceleration for one axis, given its input and current velocity
    decel, accel, brake = tuning
    if input_i == 0:
        if velocity_i > 0:
            return -decel
        if velocity_i < 0:
            return decel
        return 0.0
    if input_i * velocity_i >= 0:  # acceleration
        return accel * input_i
    return brake * input_i  # braking (reversing direction)

FACING_TURN_RATE = math.radians(360)  # max degrees/second the drone's visual facing can turn

class Plane: # the player-controlled drone: position, velocity, input, and visual facing
    def __init__(self): # spawn at a random point on the ground with zero velocity
        x = np.random.randint(0, depth)
        z = np.random.randint(0, depth)
        y = 0  # spawn on ground
        self.position = np.array([x, y, z], dtype=float)
        self.velocity = np.array([0,0,0], dtype=float)
        self.input = np.array([0, 0, 0], dtype=float)
        self.trail = deque(maxlen=40)
        self.facing_yaw = 0.0

    def set_input(self, ix, iy, iz): # called once per frame from main.py with this frame's movement intent
        self.input = np.array([ix, iy, iz], dtype=float)

    def draw_trail(self): # fading line behind the drone showing its recent path
        draw_trail(self.trail, (0.2, 0.9, 1.0))

    def update(self, dt, view_yaw=0.0): # movement settings
        accel = np.array([
            _axis_accel(self.input[0], self.velocity[0], X_Z_TUNING),
            _axis_accel(self.input[1], self.velocity[1], Y_TUNING),
            _axis_accel(self.input[2], self.velocity[2], X_Z_TUNING),])
        self.velocity += accel * dt

        self.velocity[0] = max(-drone_H_speed, min(drone_H_speed, self.velocity[0]))
        self.velocity[1] = max(-drone_V_speed, min(drone_V_speed, self.velocity[1]))
        self.velocity[2] = max(-drone_H_speed, min(drone_H_speed, self.velocity[2]))

        self.position += self.velocity * dt

        # keep the drone inside the play area
        max_pos = depth - cube
        for i in range(3):
            if self.position[i] < 0:
                self.position[i] = 0
                self.velocity[i] = 0
            elif self.position[i] > max_pos:
                self.position[i] = max_pos
                self.velocity[i] = 0

        self.trail.append(self.position.copy())

        # face the direction of travel; when nearly stationary, fall back to wherever the camera is currently looking
        horizontal_speed = math.hypot(self.velocity[0], self.velocity[2])
        target_yaw = math.atan2(self.velocity[0], self.velocity[2]) if horizontal_speed > 1.0 else view_yaw
        self.facing_yaw = smooth_yaw_towards(self.facing_yaw, target_yaw, FACING_TURN_RATE * dt)

    def draw(self): # translate to the drone's center, rotate to face facing_yaw, draw the dart
        glPushMatrix()
        glTranslatef(self.position[0] + cube/2, self.position[1] + cube/2, self.position[2] + cube/2)
        glRotatef(math.degrees(self.facing_yaw), 0, 1, 0)
        draw_dart((0.2, 0.7, 1.0))
        glPopMatrix()
