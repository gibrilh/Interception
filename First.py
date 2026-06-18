import pygame
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

def draw_axes():
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

def draw_cube():
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

class Plane:
    def __init__(self):
        self.position = np.array([0,0,0], dtype=float)
        self.velocity = np.array([0,0,0], dtype=float)
        self.acceleration = np.array([1,0,0], dtype=float)
    
    def update(self, dt):
        new_velocity = self.velocity + self.acceleration * dt
        new_position = self.position + new_velocity * dt 
        
        self.velocity = new_velocity 
        self.position = new_position
    
    def draw(self):
        glPushMatrix()
        glTranslatef(*self.position)
        draw_cube()
        glPopMatrix()

def init_gl(width, height):
    glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 200.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(20, 20, 20,
              0, 0, 0,
              0, 1, 0)

def main():
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
        glClearColor(0.1, 0.1, 0.15, 1)

        draw_axes()

        plane.update(dt)
        plane.draw()
        pygame.display.flip()

main()