import pygame
import math

class Bullet:
    def __init__(self, x, y, angle, friendly=False, speed=10, damage=1):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = 3
        self.friendly = friendly
        self.damage = damage

    def update(self):
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self, screen):
        color = (255, 255, 255) if self.friendly else (255, 255, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.size + other.size

    def is_on_screen(self, screen_width, screen_height):
        return 0 <= self.x < screen_width and 0 <= self.y < screen_height