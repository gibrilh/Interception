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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.1, 0.1, 0.15, 1)

        draw_axes()
        pygame.display.flip()
        clock.tick(60)

main()