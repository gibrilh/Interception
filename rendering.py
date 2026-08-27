import pygame
import math 
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube 
import numpy as np


_CUBE_FACES = [
    ((0, 0, -1), [(0,0,0),(0,cube,0),(cube,cube,0),(cube,0,0)]),
    ((0, 0,  1), [(0,0,cube),(cube,0,cube),(cube,cube,cube),(0,cube,cube)]),
    ((0, -1, 0), [(0,0,0),(cube,0,0),(cube,0,cube),(0,0,cube)]),
    ((0,  1, 0), [(0,cube,0),(0,cube,cube),(cube,cube,cube),(cube,cube,0)]),
    ((-1, 0, 0), [(0,0,0),(0,0,cube),(0,cube,cube),(0,cube,0)]),
    (( 1, 0, 0), [(cube,0,0),(cube,cube,0),(cube,cube,cube),(cube,0,cube)]),]

def draw_cube_wireframe():
    glBegin(GL_LINES)
    for _, verts in _CUBE_FACES:
        for i in range(4):
            glVertex3f(*verts[i])
            glVertex3f(*verts[(i + 1) % 4])
    glEnd()

def draw_solid_cube(color=(0.2, 0.6, 1.0)):
    glColor3f(*color)
    glBegin(GL_QUADS)
    for normal, verts in _CUBE_FACES:
        glNormal3f(*normal)
        for v in verts:
            glVertex3f(*v)
    glEnd()

    # crisp outline for a stylized look
    glDisable(GL_LIGHTING)
    glColor3f(0, 0, 0)
    glLineWidth(1.5)
    draw_cube_wireframe()
    glEnable(GL_LIGHTING)

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
    glColor3f(0.5, 0.8, 1.0)
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

def draw_text(x, y, text, screen_width=800, screen_height=600, color=(0, 0, 0)):
    font = pygame.font.SysFont('monospace', 18)
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, 'RGBA', True)
    w, h = text_surface.get_size()

    # switch to 2D mode
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    glDisable(GL_FOG)

    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()

    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glEnable(GL_DEPTH_TEST)
    glDeleteTextures([tex])

    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()

def draw_ground_grid(depth, spacing=5):
    glBegin(GL_LINES)
    glColor3f(0.3, 0.5, 0.3)  # darker green than background
    for i in range(0, depth + 1, spacing):
        # lines along X
        glVertex3f(0, 0, i)
        glVertex3f(depth, 0, i)
        # lines along Z
        glVertex3f(i, 0, 0)
        glVertex3f(i, 0, depth)
    for i in range(0, depth + 1, spacing):
        # lines along X
        glVertex3f(0, i, 0)
        glVertex3f(depth, i, 0)
        # lines along Y
        glVertex3f(i, 0, 0)
        glVertex3f(i, depth, 0)
    for i in range(0, depth + 1, spacing):
        # lines along Z
        glVertex3f(depth, 0, i)
        glVertex3f(depth, depth, i)
        # lines along Y
        glVertex3f(depth, i, 0)
        glVertex3f(depth, i, depth)
    glEnd()

def draw_shadow(position):
    x, y, z = position
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.3, 0.1)  # dark green
    glVertex3f(x,        0.1, z)
    glVertex3f(x + cube, 0.1, z)
    glVertex3f(x + cube, 0.1, z + cube)
    glVertex3f(x,        0.1, z + cube)
    glEnd()

def draw_altitude_line(position):
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(position[0] + cube/2, position[1], position[2] + cube/2)
    glVertex3f(position[0] + cube/2, 0,           position[2] + cube/2)
    glEnd()

def draw_game_over_screen(win):
    if win:
        draw_text(300, 350, "YOU WIN")
    else:
        draw_text(300, 350, "GAME OVER")
    draw_text(300, 300, "Click to Restart")

def draw_danger_overlay(intensity, screen_width=800, screen_height=600):
    if intensity <= 0:
        return
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(1, 0, 0, intensity)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(screen_width, 0)
    glVertex2f(screen_width, screen_height); glVertex2f(0, screen_height)
    glEnd()
    glDisable(GL_BLEND); glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()

def draw_compass(plane_pos, target_pos, view_yaw, color=(0,1,0), screen_width=800, screen_height=600):
    dx, dz = target_pos[0]-plane_pos[0], target_pos[2]-plane_pos[2]
    target_bearing = math.atan2(dx, dz)
    rel = target_bearing - view_yaw  # angle of the target relative to where we're currently facing

    cx, cy, r = screen_width/2, screen_height-70, 28
    # dir points "up" (ahead) on screen when rel==0, swings right/left to match which way to turn
    dirx, diry = -math.sin(rel), math.cos(rel)
    perpx, perpy = diry, -dirx

    tip  = (cx + dirx*r, cy + diry*r)
    base_l = (cx + dirx*r*0.25 + perpx*r*0.45, cy + diry*r*0.25 + perpy*r*0.45)
    base_r = (cx + dirx*r*0.25 - perpx*r*0.45, cy + diry*r*0.25 - perpy*r*0.45)
    tail   = (cx - dirx*r*0.5, cy - diry*r*0.5)

    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, screen_width, 0, screen_height, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_FOG)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # dial ring
    glColor4f(0, 0, 0, 0.35)
    glBegin(GL_LINE_LOOP)
    for i in range(28):
        a = 2*math.pi*i/28
        glVertex2f(cx + r*1.15*math.cos(a), cy + r*1.15*math.sin(a))
    glEnd()

    # arrowhead (filled triangle) + tail (thin shaft), like a compass needle
    glColor3f(*color)
    glBegin(GL_TRIANGLES)
    glVertex2f(*tip); glVertex2f(*base_l); glVertex2f(*base_r)
    glEnd()
    glLineWidth(2.0)
    glBegin(GL_LINES); glVertex2f(cx, cy); glVertex2f(*tail); glEnd()

    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST); glEnable(GL_FOG)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()