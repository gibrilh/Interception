import pygame
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

# important variables 
depth = 200 # for window settings 

def draw_axes(): # drawing axes 
    glBegin(GL_LINES)
    glColor3f(1, 0, 0) # red 
    glVertex3f(0, 0, 0)
    glVertex3f(10, 0, 0)

    glColor3f(0, 1, 0) # green 
    glVertex3f(0, 0, 0)
    glVertex3f(0, 10, 0)

    glColor3f(0, 0, 1) # blue
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 10)

    glEnd()

def draw_cube():  # drawing cube 
    glBegin(GL_LINES)
    glColor3f(0, 1, 1)
    glVertex3f(0, 0, 0)
    glVertex3f(0, 0, 10)

    glVertex3f(0, 0, 0)
    glVertex3f(0, 10, 0)

    glVertex3f(0, 0, 0)
    glVertex3f(10, 0, 0)

    glVertex3f(0, 0, 10)
    glVertex3f(0, 10, 10)

    glVertex3f(0, 10, 0)
    glVertex3f(0, 10, 10)

    glVertex3f(10, 0, 0)
    glVertex3f(10, 10, 0)

    glVertex3f(10, 10, 0)
    glVertex3f(10, 10, 10)

    glVertex3f(0, 10, 10)
    glVertex3f(10, 10, 10)

    glVertex3f(0, 10, 0)
    glVertex3f(10, 10, 0)

    glVertex3f(0, 0, 10)
    glVertex3f(10, 0, 10)

    glVertex3f(10, 0, 10)
    glVertex3f(10, 10, 10)

    glVertex3f(10, 0, 0)
    glVertex3f(10, 0, 10)
    
    glEnd()

class Plane: # plane variables that get updated 
    def __init__(self):
        self.position = np.array([0,0,0], dtype=float)
        self.velocity = np.array([0,0,0], dtype=float)
        self.acceleration = np.array([0,0,0], dtype=float)
    
    def update(self, dt): # movement settings 
        drag = self.velocity * -1 
        net_acceleration = self.acceleration + drag
        new_velocity = self.velocity + net_acceleration * dt 
        new_position = self.position + new_velocity * dt
        
        self.velocity = new_velocity 
        self.position = new_position

        if self.position[1] < 0: # ground settings 
            self.position[1] = 0
            self.velocity[1] = 0
    
    def draw(self): # drawing the cube 
        glPushMatrix()
        glTranslatef(*self.position)
        draw_cube()
        glPopMatrix()

def init_gl(width, height):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 2000.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, depth,
              0, 50, 0,
              0, 1, 0)

def background(depth):
    # sky
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(-depth*3,      0, -1)
    glVertex3f( depth*3,      0, -1)
    glVertex3f( depth*3,  depth*3, -1)
    glVertex3f(-depth*3,  depth*3, -1)
    glEnd()

    # ground
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.6, 0.2)
    glVertex3f(-depth*3,       0, -1)
    glVertex3f( depth*3,       0, -1)
    glVertex3f( depth*3, -depth*3, -1)
    glVertex3f(-depth*3, -depth*3, -1)
    glEnd()

def main(): # window settings
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
        glClearColor(0, 0, 0, 1)
        background(depth)
        draw_axes()

        keys = pygame.key.get_pressed()

        ax = 0
        ay = 0 
        az = 0 

        if keys[pygame.K_d]:
            ax = 50
        if keys[pygame.K_a]:
            ax = -50
        if keys[pygame.K_w]:
            ay = 50
        if keys[pygame.K_s]:
            ay = -50
        plane.acceleration = np.array([ax, ay, az], dtype=float)

        plane.update(dt)
        plane.draw()
        pygame.display.flip()

main()