import pygame
import math
import random

class Enemy:
    def __init__(self, enemy_type, arena_rect):
        self.type = enemy_type
        self.size = 30 if enemy_type == "boss" else 15
        self.arena_rect = arena_rect
        self.x, self.y = self.get_spawn_position()
        self.health = 50 if enemy_type == "boss" else (3 if enemy_type == "tough" else 1)
        self.score_value = 100 if enemy_type == "boss" else (30 if enemy_type == "tough" else 10)

    def get_spawn_position(self):
        side = random.choice(['top', 'bottom', 'left', 'right'])
        if side == 'top':
            return random.randint(self.arena_rect.left, self.arena_rect.right), self.arena_rect.top
        elif side == 'bottom':
            return random.randint(self.arena_rect.left, self.arena_rect.right), self.arena_rect.bottom
        elif side == 'left':
            return self.arena_rect.left, random.randint(self.arena_rect.top, self.arena_rect.bottom)
        else:
            return self.arena_rect.right, random.randint(self.arena_rect.top, self.arena_rect.bottom)

    def take_damage(self, amount):
        self.health -= amount

    def draw(self, screen, boss_color, enemy_color):
        color = boss_color if self.type == "boss" else enemy_color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.size + other.size

    def is_on_screen(self):
        return self.arena_rect.collidepoint(self.x, self.y)