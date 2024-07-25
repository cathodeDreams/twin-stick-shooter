import pygame
import math
import random

class Enemy:
    def __init__(self, enemy_type, screen_width, screen_height):
        self.type = enemy_type
        self.size = 30 if enemy_type == "boss" else 15
        self.x, self.y = self.get_spawn_position(screen_width, screen_height)
        self.health = 50 if enemy_type == "boss" else (3 if enemy_type == "tough" else 1)
        self.score_value = 100 if enemy_type == "boss" else (30 if enemy_type == "tough" else 10)

    def get_spawn_position(self, screen_width, screen_height):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return random.randint(0, screen_width), 0
        elif side == 'bottom':
            return random.randint(0, screen_width), screen_height
        elif side == 'left':
            return 0, random.randint(0, screen_height)
        else:
            return screen_width, random.randint(0, screen_height)

    def take_damage(self, amount):
        self.health -= amount

    def draw(self, screen):
        color = (255, 0, 0) if self.type == "boss" else (200, 0, 0)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.size + other.size

    def is_on_screen(self, screen_width, screen_height):
        return 0 <= self.x < screen_width and 0 <= self.y < screen_height