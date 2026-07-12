import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# important variables 
depth = 200 # for window settings 
cube = 10

def draw_axes(): # edges
    glBegin(GL_LINES)
    glColor3f(0, 0, 0)

    # bottom face
    glVertex3f(0, 0, 0)
    glVertex3f(depth-1, 0, 0)

    glVertex3f(depth-1, 0, 0)
    glVertex3f(depth-1, 0, depth-1)

    glVertex3f(depth-1, 0, depth-1)
    glVertex3f(0, 0, depth-1)

    glVertex3f(0, 0, depth-1)
    glVertex3f(0, 0, 0)

    # top face
    glVertex3f(0, depth-1, 0)
    glVertex3f(depth-1, depth-1, 0)

    glVertex3f(depth-1, depth-1, 0)
    glVertex3f(depth-1, depth-1, depth-1)

    glVertex3f(depth-1, depth-1, depth-1)
    glVertex3f(0, depth-1, depth-1)

    glVertex3f(0, depth-1, depth-1)
    glVertex3f(0, depth-1, 0)

    # vertical edges
    glVertex3f(0, 0, 0)
    glVertex3f(0, depth-1, 0)

    glVertex3f(depth-1, 0, 0)
    glVertex3f(depth-1, depth-1, 0)

    glVertex3f(depth-1, 0, depth-1)
    glVertex3f(depth-1, depth-1, depth-1)

    glVertex3f(0, 0, depth-1)
    glVertex3f(0, depth-1, depth-1)

    glEnd()

def draw_cube():  # drawing cube 
    glBegin(GL_LINES)
    glColor3f(0, 1, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, cube)

    glVertex3f(0, 0, 0)
    glVertex3f(0, cube, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(cube, 0, 0)

    glVertex3f(0, 0, cube)
    glVertex3f(0, cube, cube)

    glVertex3f(0, cube, 0)
    glVertex3f(0, cube, cube)

    glVertex3f(cube, 0, 0)
    glVertex3f(cube, cube, 0)

    glVertex3f(cube, cube, 0)
    glVertex3f(cube, cube, cube)

    glVertex3f(0, cube, cube)
    glVertex3f(cube, cube, cube)

    glVertex3f(0, cube, 0)
    glVertex3f(cube, cube, 0)

    glVertex3f(0, 0, cube)
    glVertex3f(cube, 0, cube)

    glVertex3f(cube, 0, cube)
    glVertex3f(cube, cube, cube)

    glVertex3f(cube, 0, 0)
    glVertex3f(cube, 0, cube)
    
    glEnd()

class Plane: # plane variables that get updated 
    def __init__(self):
        self.position = np.array([0,0,0], dtype=float)
        self.velocity = np.array([0,0,0], dtype=float)
        self.acceleration = np.array([0,0,0], dtype=float)
    
    def update(self, dt): # movement settings 
        drag = self.velocity * -1 
        gravity = np.array([0, -9.8, 0], dtype=float)
        net_acceleration = self.acceleration + drag + gravity
        new_velocity = self.velocity + net_acceleration * dt 
        new_position = self.position + new_velocity * dt
        
        self.velocity = new_velocity 
        self.position = new_position

        # boundary settings 
        if self.position[0] < 0:
            self.position[0] = 0
            self.velocity[0] = 0

        if self.position[0] > depth - cube : # ground settings d
            self.position[0] = depth - cube 
            self.velocity[0] = 0

        if self.position[1] < 0:
            self.position[1] = 0
            self.velocity[1] = 0

        if self.position[1] > depth - cube : # ground settings 
            self.position[1] = depth - cube 
            self.velocity[1] = 0

        if self.position[2] < 0:
            self.position[2] = 0
            self.velocity[2] = 0

        if self.position[2] > depth - cube : # ground settings 
            self.position[2] = depth - cube 
            self.velocity[2] = 0
    
    def draw(self): # drawing the cube 
        glPushMatrix()
        glTranslatef(*self.position)
        draw_cube()
        glPopMatrix()

# camera settings for it to be moved 
cam_yaw = 0.0       # horizontal angle in radians
cam_pitch = 0.3     # vertical angle in radians
cam_distance = 200  # zoom level

def get_camera_position():
    x = cam_distance * math.cos(cam_pitch) * math.sin(cam_yaw)
    y = cam_distance * math.sin(cam_pitch)
    z = cam_distance * math.cos(cam_pitch) * math.cos(cam_yaw)
    return x, y, z

def init_gl(width, height):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 2000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def background(depth):
    # sky 1 
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(0,      0, 0)
    glVertex3f( depth,      0, 0)
    glVertex3f( depth,  depth, 0)
    glVertex3f(0,  depth, 0)
    glEnd()

    # sky 2 
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(depth, 0,       0)
    glVertex3f(depth, 0,       depth)
    glVertex3f(depth, depth, depth)
    glVertex3f(depth, depth, 0)
    glEnd()

    # ground
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.6, 0.2)
    glVertex3f(0, 0, 0)
    glVertex3f( depth, 0, 0)
    glVertex3f( depth, 0,  depth)
    glVertex3f(0, 0,  depth)
    glEnd()

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