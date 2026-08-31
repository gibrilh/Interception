#drawing helpers, used by every other module. Grouped as:
#   - draw_dart: the directional shape used for both drone and interceptor
#   - draw_trail: fading path line (drone/interceptor)
#   - background, draw_ground_grid, draw_shadow, draw_altitude_line*: world backdrop
#   - draw_text, _draw_hud_panel: shared 2D-overlay primitives
#   - draw_hud, draw_goal_distance, draw_time_hud, draw_compass,
#     draw_danger_overlay, draw_game_over_screen: HUD, built on those primitives

import pygame
import math
import sys
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from constants import depth, cube, ScreenW, ScreenH, goal_radius
import numpy as np

_half = cube / 2
_DART_BASE = [(-_half, -_half, -_half), (_half, -_half, -_half), (_half, _half, -_half), (-_half, _half, -_half)]
_DART_TIP = (0, 0, _half * 2.2)  # nose pokes out past the body so the shape reads as directional

def _face_normal(v0, v1, v2): # outward normal of a triangle, for lighting
    a = np.subtract(v1, v0)
    b = np.subtract(v2, v0)
    n = np.cross(a, b)
    m = np.linalg.norm(n)
    return tuple(n / m) if m > 0 else (0, 0, 1)

def draw_dart(color=(0.2, 0.6, 1.0)): # lit body + black wireframe outline, pointed nose so rotation is visible
    b0, b1, b2, b3 = _DART_BASE
    tip = _DART_TIP

    glColor3f(*color)
    glBegin(GL_QUADS)
    glNormal3f(0, 0, -1)
    glVertex3f(*b0); glVertex3f(*b3); glVertex3f(*b2); glVertex3f(*b1)
    glEnd()

    glBegin(GL_TRIANGLES)
    for v0, v1 in [(b0, b1), (b1, b2), (b2, b3), (b3, b0)]:
        glNormal3f(*_face_normal(v0, v1, tip))
        glVertex3f(*v0); glVertex3f(*v1); glVertex3f(*tip)
    glEnd()

    glDisable(GL_LIGHTING)
    glColor3f(0, 0, 0)
    glLineWidth(1.5)
    glBegin(GL_LINES)
    for v0, v1 in [(b0, b1), (b1, b2), (b2, b3), (b3, b0), (b0, tip), (b1, tip), (b2, tip), (b3, tip)]:
        glVertex3f(*v0); glVertex3f(*v1)
    glEnd()
    glEnable(GL_LIGHTING)

def draw_trail(trail, color, alpha_scale=0.8): # fading line strip through a deque of past positions
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    n = len(trail)
    glBegin(GL_LINE_STRIP)
    for i, p in enumerate(trail):
        a = i / max(1, n)
        glColor4f(color[0], color[1], color[2], a * alpha_scale)
        glVertex3f(p[0] + cube/2, p[1] + cube/2, p[2] + cube/2)
    glEnd()
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def background(depth): # sky (two panels) + ground quad, filling the arena's bounding faces
    # sky 1
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.7, 1.0)
    glVertex3f(0, 0, 0)
    glVertex3f( depth, 0, 0)
    glVertex3f( depth, depth, 0)
    glVertex3f(0, depth, 0)
    glEnd()

    # sky 2
    glBegin(GL_QUADS)
    glColor3f(0.5, 0.8, 1.0)
    glVertex3f(depth, 0, 0)
    glVertex3f(depth, 0, depth)
    glVertex3f(depth, depth, depth)
    glVertex3f(depth, depth, 0)
    glEnd()

    # ground
    glBegin(GL_QUADS)
    glColor3f(0.2, 0.6, 0.2)
    glVertex3f(0, 0, 0)
    glVertex3f( depth, 0, 0)
    glVertex3f( depth, 0, depth)
    glVertex3f(0, 0, depth)
    glEnd()

def draw_text(x, y, text, color=(0, 0, 0), bold=False): # renders text to a texture, draws it as a 2D quad
    font = pygame.font.SysFont('monospace', 18, bold=bold)
    text_surface = font.render(text, True, color)
    text_data = pygame.image.tostring(text_surface, 'RGBA', True)
    w, h = text_surface.get_size()

    # switch to 2D mode
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, ScreenW, 0, ScreenH, -1, 1)
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
    # GL_MODULATE (the default) multiplies the texture by the last glColor -
    # reset to white so the text's own baked-in color actually shows
    glColor4f(1, 1, 1, 1)

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

def draw_ground_grid(depth, spacing=5): # wireframe grid over all three arena bounding faces
    glBegin(GL_LINES)
    glColor3f(0.3, 0.5, 0.3)  # darker green than background
    for i in range(0, depth + 1, spacing):
        glVertex3f(0, 0, i)
        glVertex3f(depth, 0, i)
        glVertex3f(i, 0, 0)
        glVertex3f(i, 0, depth)
    for i in range(0, depth + 1, spacing):
        glVertex3f(0, i, 0)
        glVertex3f(depth, i, 0)
        glVertex3f(i, 0, 0)
        glVertex3f(i, depth, 0)
    for i in range(0, depth + 1, spacing):
        glVertex3f(depth, 0, i)
        glVertex3f(depth, depth, i)
        glVertex3f(depth, i, 0)
        glVertex3f(depth, i, depth)
    glEnd()

def draw_shadow(position): # flat dark quad on the ground under the drone
    x, y, z = position
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.3, 0.1)  # dark green
    glVertex3f(x, 0.1, z)
    glVertex3f(x + cube, 0.1, z)
    glVertex3f(x + cube, 0.1, z + cube)
    glVertex3f(x, 0.1, z + cube)
    glEnd()

def draw_altitude_line(position): # red line from the drone straight down to the ground
    glBegin(GL_LINES)
    glColor3f(1, 0, 0)
    glVertex3f(position[0] + cube/2, position[1], position[2] + cube/2)
    glVertex3f(position[0] + cube/2, 0, position[2] + cube/2)
    glEnd()

def draw_goal_altitude_line(position, color=(0, 1, 0), alpha=0.4): # same idea, faint green, for the goal
    glDisable(GL_LIGHTING)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(color[0], color[1], color[2], alpha)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    glVertex3f(position[0], position[1], position[2])
    glVertex3f(position[0], 0, position[2])
    glEnd()
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING)

def _draw_hud_panel(x, y, w, h, color=(0, 0, 0), alpha=0.55): # translucent backing plate so HUD text stays legible over anything
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, ScreenW, 0, ScreenH, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING); glDisable(GL_FOG)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(color[0], color[1], color[2], alpha)
    glBegin(GL_QUADS)
    glVertex2f(x, y); glVertex2f(x + w, y); glVertex2f(x + w, y + h); glVertex2f(x, y + h)
    glEnd()
    glDisable(GL_BLEND)
    glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST); glEnable(GL_FOG)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()

def draw_hud(speed, altitude): # speed panel bottom-left, altitude panel bottom-right
    panel_w, panel_h = 200, 50
    margin = 24
    y = margin

    _draw_hud_panel(margin, y, panel_w, panel_h)
    draw_text(margin + 16, y + 14, f"SPEED {speed:5.1f}", color=(255, 255, 255), bold=True)

    x = ScreenW - margin - panel_w
    _draw_hud_panel(x, y, panel_w, panel_h)
    draw_text(x + 16, y + 14, f"ALT   {altitude:5.1f}", color=(255, 255, 255), bold=True)

def draw_game_over_screen(win): # centered win/lose text + restart prompt
    if win:
        draw_text(300, 350, "YOU WIN")
    else:
        draw_text(300, 350, "GAME OVER")
    draw_text(300, 300, "Click to Restart")

def draw_danger_overlay(intensity, color=(1, 0, 0)): # fullscreen translucent flash (interceptor lock / warning zone)
    if intensity <= 0:
        return
    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, ScreenW, 0, ScreenH, -1, 1)
    glMatrixMode(GL_MODELVIEW); glPushMatrix(); glLoadIdentity()
    glDisable(GL_DEPTH_TEST); glDisable(GL_LIGHTING)
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(color[0], color[1], color[2], intensity)
    glBegin(GL_QUADS)
    glVertex2f(0, 0); glVertex2f(ScreenW, 0)
    glVertex2f(ScreenW, ScreenH); glVertex2f(0, ScreenH)
    glEnd()
    glDisable(GL_BLEND); glEnable(GL_LIGHTING); glEnable(GL_DEPTH_TEST)
    glMatrixMode(GL_PROJECTION); glPopMatrix()
    glMatrixMode(GL_MODELVIEW); glPopMatrix()

def draw_goal_distance(distance): # HUD panel below the compass - distance to the goal's surface
    panel_w, panel_h = 180, 40
    x = ScreenW/2 - panel_w/2
    y = ScreenH - 155

    _draw_hud_panel(x, y, panel_w, panel_h)
    draw_text(x + 16, y + 11, f"GOAL {(distance - goal_radius):5.1f}m", color=(255, 255, 255), bold=True)

def draw_time_hud(time_left, low_threshold=5.0): # HUD panel below draw_goal_distance - flashes red when low
    panel_w, panel_h = 180, 40
    x = ScreenW/2 - panel_w/2
    y = ScreenH - 205

    text_color = (255, 255, 255)
    if time_left <= low_threshold:
        flash = abs(math.sin(pygame.time.get_ticks() / 1000 * 6))
        text_color = (255, 70, 70) if flash > 0.5 else (255, 255, 255)

    _draw_hud_panel(x, y, panel_w, panel_h)
    draw_text(x + 16, y + 11, f"TIME {time_left:5.1f}", color=text_color, bold=True)

def draw_compass(plane_pos, target_pos, view_yaw, color=(0,1,0)): # needle pointing at the goal, relative to view_yaw
    dx, dz = target_pos[0]-plane_pos[0], target_pos[2]-plane_pos[2]
    target_bearing = math.atan2(dx, dz)
    rel = target_bearing - view_yaw

    cx, cy, r = ScreenW/2, ScreenH-70, 28
    dirx, diry = -math.sin(rel), math.cos(rel)
    perpx, perpy = diry, -dirx

    tip  = (cx + dirx*r, cy + diry*r)
    base_l = (cx + dirx*r*0.25 + perpx*r*0.45, cy + diry*r*0.25 + perpy*r*0.45)
    base_r = (cx + dirx*r*0.25 - perpx*r*0.45, cy + diry*r*0.25 - perpy*r*0.45)
    tail   = (cx - dirx*r*0.5, cy - diry*r*0.5)

    glMatrixMode(GL_PROJECTION); glPushMatrix(); glLoadIdentity()
    glOrtho(0, ScreenW, 0, ScreenH, -1, 1)
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

    # arrowhead (filled triangle) + tail (thin shaft)
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
