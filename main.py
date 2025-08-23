from __future__ import annotations
import pygame
from pygame.math import Vector2

class Point:
    def __init__(self, pos: Vector2) -> None:
        self.pos = pos
        self.vel = Vector2(0,0)
    
    def update(self, points: list[Point]):
        pass

pygame.init()
screen = pygame.display.set_mode((500,500))
clock = pygame.Clock()

points = []

delta = 0
on = True
while on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            on = False
    
    

    pygame.display.flip()
    delta = clock.tick(60)