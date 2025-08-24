from __future__ import annotations
import pygame, numpy, math, random
from pygame.math import Vector2

DRAG = 30
GRAVITY = 150
REPEL = 300
MOUSE_FORCE = 500

SIZE = 500
D_SCALE = 10
D_SIZE = SIZE // D_SCALE
REV_SCALE = SIZE / D_SIZE

def scale(pos: float) -> int:
    return min(D_SIZE-1,math.floor(pos//D_SCALE))

i = 0
class Point:
    def __init__(self, pos: Vector2) -> None:
        global i
        self.pos = pos
        self.vel = Vector2(0,0)
        self.id = i
        i += 1
    
    def update(self, distribution: numpy.ndarray, delta: float, mouse: Vector2 | None, push: bool):
        add_vel = Vector2(0,GRAVITY)

        if self.vel.x > 0:
            add_vel.x -= max(self.vel.x, DRAG)
        elif self.vel.x < 0:
            add_vel.x += max(-self.vel.x, DRAG)
        if self.vel.y > 0:
            add_vel.y -= max(self.vel.y, DRAG)
        elif self.vel.y < 0:
            add_vel.y += max(-self.vel.y, DRAG)
        
        min_score = 999
        zero = 0
        direction = [Vector2(0,0)]
        x, y = scale(self.pos.x), scale(self.pos.y)
        for rel_x in (0, 1, -1):
            for rel_y in (1, 0, -1):
                if rel_x == 0 and rel_y == 0:
                    zero = distribution[x, y]
                elif x + rel_x >= 0 and x + rel_x < D_SIZE and y + rel_y >= 0 and y + rel_y < D_SIZE:
                    score = distribution[x + rel_x, y + rel_y]
                    if score < min_score:
                        direction = [Vector2(rel_x, rel_y)]
                        min_score = score
                    elif score == min_score:
                        direction.append(Vector2(rel_x, rel_y))
        if zero > min_score:
            add_vel += random.choice(direction) * REPEL * math.log(zero - min_score, 5)

        if mouse is not None:
            if push:
                add_vel -= (mouse - self.pos).normalize() * MOUSE_FORCE * 0.6 ** (mouse.distance_to(self.pos) * 0.03)
            else:
                add_vel += (mouse - self.pos).normalize() * MOUSE_FORCE * math.log10(mouse.distance_to(self.pos))

        add_vel *= delta * 0.5
        self.vel += add_vel
        self.pos += self.vel * delta
        self.vel += add_vel
        if self.pos.x < 0:
            self.pos.x = 0
            if self.vel.x < 0: self.vel.x = 0
        if self.pos.y < 0:
            self.pos.y = 0
            if self.vel.y < 0: self.vel.y = 0
        if self.pos.x > SIZE - 1:
            self.pos.x = SIZE - 1
            if self.vel.x > 0: self.vel.x = 0
        if self.pos.y > SIZE - 1:
            self.pos.y = SIZE - 1
            if self.vel.y > 0: self.vel.y = 0

pygame.init()
screen = pygame.display.set_mode((SIZE,SIZE), pygame.NOFRAME)
clock = pygame.Clock()

points = [Point(Vector2(x,y)) for x in range(10, 496, 2) for y in range(250, 275, 5)]

delta = 0
on = True
while on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            on = False
    
    screen.fill((22,22,22))

    distribution = numpy.ndarray((D_SIZE,D_SIZE), int)
    distribution.fill(0)
    for p in points: distribution[scale(p.pos.x), scale(p.pos.y)] += 1

    mouse_pressed = pygame.mouse.get_pressed()
    mouse = None
    push = False
    if mouse_pressed[0]:
        mouse = Vector2(pygame.mouse.get_pos())
    elif mouse_pressed[2]:
        mouse = Vector2(pygame.mouse.get_pos())
        push = True

    for p in points: p.update(distribution, delta, mouse, push)
        # pygame.draw.circle(screen, (30,30,150), p.pos, 2)

    for x in range(D_SIZE):
        for y in range(D_SIZE):
            v = distribution[x, y]
            if v > 0:
                pygame.draw.rect(screen, (min(15+5*v,50),min(15+5*v,50),min(60+15*v,255)), (x * REV_SCALE, y * REV_SCALE, REV_SCALE, REV_SCALE))

    pygame.display.flip()
    delta = clock.tick(60) / 1000