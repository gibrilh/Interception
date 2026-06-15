import pygame
import sys
import numpy as np

pygame.init()

screen = pygame.display.set_mode((800,600))
pygame.display.set_caption("missile simulation")

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    screen.fill((255,255,255))
    pygame.display.flip()
    clock.tick(60)