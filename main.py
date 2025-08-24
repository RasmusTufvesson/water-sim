from __future__ import annotations
import pygame, numpy, math, random
from pygame.math import Vector2

DRAG = 30
GRAVITY = 300
REPEL = 300
MOUSE_FORCE = 500
OBJ_DENSITY = 10

SIZE = 500
D_SCALE = 10
D_SIZE = SIZE // D_SCALE
REV_SCALE = SIZE / D_SIZE

def scale(pos: float) -> int:
    return max(min(D_SIZE-1,math.floor(pos//D_SCALE)),0)

i = 0
class Point:
    def __init__(self, pos: Vector2) -> None:
        global i
        self.pos = pos
        self.vel = Vector2(0,0)
        self.id = i
        i += 1
    
    def update(self, distribution: numpy.ndarray, delta: float, mouse: Vector2 | None, push: bool, mul: float):
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
                    zero = distribution[x, y] - 1
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
                add_vel -= (mouse - self.pos).normalize() * MOUSE_FORCE * mul * 0.6 ** (mouse.distance_to(self.pos) * 0.03)
            else:
                add_vel += (mouse - self.pos).normalize() * MOUSE_FORCE * mul * math.log10(mouse.distance_to(self.pos))

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

class Circle:
    def __init__(self, pos: Vector2, radius: float) -> None:
        global i
        self.pos = pos
        self.vel = Vector2(0,0)
        self.radius = radius
        self.tile_radius = self.radius / D_SCALE
        self.id = i
        i += 1
    
    def update(self, distribution: numpy.ndarray, delta: float, mouse: Vector2 | None):
        if mouse is not None:
            self.vel = (mouse - self.pos) / delta
            self.pos = mouse
        else:
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
                    rel_x = rel_x * self.tile_radius
                    rel_y = rel_y * self.tile_radius
                    if rel_x == 0 and rel_y == 0:
                        zero = distribution[x, y] - 1
                    elif x + rel_x >= 0 and x + rel_x < D_SIZE and y + rel_y >= 0 and y + rel_y < D_SIZE:
                        score = distribution[math.floor(x + rel_x), math.floor(y + rel_y)]
                        if score < min_score:
                            direction = [Vector2(rel_x, rel_y)]
                            min_score = score
                        elif score == min_score:
                            direction.append(Vector2(rel_x, rel_y))
            if zero > min_score:
                add_vel += random.choice(direction) * REPEL * math.log(zero - min_score, 5)

            add_vel *= delta * 0.5
            self.vel += add_vel
            self.pos += self.vel * delta
            self.vel += add_vel

        if self.pos.x < self.radius:
            self.pos.x = self.radius
            if self.vel.x < 0: self.vel.x = 0
        if self.pos.y < self.radius:
            self.pos.y = self.radius
            if self.vel.y < 0: self.vel.y = 0
        if self.pos.x > SIZE - 1 - self.radius:
            self.pos.x = SIZE - 1 - self.radius
            if self.vel.x > 0: self.vel.x = 0
        if self.pos.y > SIZE - 1 - self.radius:
            self.pos.y = SIZE - 1 - self.radius
            if self.vel.y > 0: self.vel.y = 0

    def to_distribution(self, distribution: numpy.ndarray):
        for x in range(int(self.radius*2)):
            for y in range(int(self.radius*2)):
                if Vector2(x-self.radius,y-self.radius).magnitude() < self.radius:
                    distribution[scale(self.pos.x - self.radius + x), scale(self.pos.y - self.radius + y)] += OBJ_DENSITY
    
    def collides(self, pos: Vector2) -> bool:
        return pos.distance_to(self.pos) <= self.radius

pygame.init()
screen = pygame.display.set_mode((SIZE,SIZE), pygame.NOFRAME)
clock = pygame.Clock()

points = [Point(Vector2(x,y)) for x in range(10, 496, 2) for y in range(250, 285, 5)]
objects: list[Circle] = []

font = pygame.font.SysFont("Arial", 14)
fps_buffer = []
show_fps = False

mouse_force_mul = 1
drag_object = None
push = False
drag_water = False
spawn_water = False

delta = 0
on = True
while on:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            on = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                show_fps = not show_fps
            elif event.key == pygame.K_LSHIFT:
                mouse_force_mul *= 0.4
            elif event.key == pygame.K_LCTRL:
                mouse_force_mul *= 1.5
            elif event.key == pygame.K_1: objects.append(Circle(Vector2(pygame.mouse.get_pos()), 10))
            elif event.key == pygame.K_2: objects.append(Circle(Vector2(pygame.mouse.get_pos()), 20))
            elif event.key == pygame.K_3: objects.append(Circle(Vector2(pygame.mouse.get_pos()), 30))
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_LSHIFT:
                mouse_force_mul /= 0.4
            elif event.key == pygame.K_LCTRL:
                mouse_force_mul /= 1.5
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = Vector2(pygame.mouse.get_pos())
                for o in objects:
                    if o.collides(mouse_pos):
                        drag_object = o.id
                        break
                else:
                    drag_water = True
                    push = False
            elif event.button == 3:
                drag_water = True
                push = True
            elif event.button == 2:
                spawn_water = True
        elif event.type == pygame.MOUSEBUTTONUP:
            drag_object = None
            drag_water = False
            spawn_water = False
    
    screen.fill((22,22,22))

    distribution = numpy.ndarray((D_SIZE,D_SIZE), int)
    distribution.fill(0)
    for p in points: distribution[scale(p.pos.x), scale(p.pos.y)] += 1

    mouse_pos = Vector2(pygame.mouse.get_pos())
    if spawn_water:
        for _ in range(3): points.append(Point(Vector2(pygame.mouse.get_pos())))

    for o in objects: o.update(distribution, delta, mouse_pos if drag_object == o.id else None)
    for o in objects: o.to_distribution(distribution)

    for p in points: p.update(distribution, delta, mouse_pos if drag_water else None, push, mouse_force_mul)
        # pygame.draw.circle(screen, (30,30,150), p.pos, 2)

    for x in range(D_SIZE):
        for y in range(D_SIZE):
            v = distribution[x, y]
            if v > 0:
                pygame.draw.rect(screen, (min(13+2*v,50),min(13+2*v,50),min(50+5*v,255)), (x * REV_SCALE, y * REV_SCALE, REV_SCALE, REV_SCALE))

    if show_fps:
        fps = math.floor(1 / (sum(fps_buffer) / len(fps_buffer)))
        text = font.render(str(fps), True, (200,200,200))
        screen.blit(text, text.get_rect(bottomleft=(0,SIZE)))

    pygame.display.flip()
    delta = clock.tick(60) / 1000
    if len(fps_buffer) > 20: fps_buffer.pop()
    fps_buffer.append(delta)