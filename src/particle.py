import pygame
import math
from colors import Colors

class Particle:
    def __init__(self, x, y, angle, speed, lifetime):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.lifetime = lifetime
        self.size = 3
        self.color = Colors.FOREGROUND  # Using the new color scheme

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)
        self.lifetime -= 1

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)