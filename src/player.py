import pygame
import math
import random
from bullet import Bullet

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 20
        self.hitbox_size = 5  # New smaller hitbox size
        self.speed = 5
        self.angle = 0
        self.alive = True
        self.shield_active = False
        self.shield_timer = 0
        self.hits_remaining = 1
        self.current_weapon = "default"
        self.fire_cooldown = 0
        self.fire_rate = 15  # Frames between shots
        self.sword_cooldown = 0
        self.sword_cooldown_max = 30  # 0.5 seconds at 60 FPS
        self.sword_range = 50
        self.sword_damage = 5
        self.powerup_timer = 0

    def move(self, dx, dy, screen_width, screen_height):
        self.x = max(self.size, min(screen_width - self.size, self.x + dx * self.speed))
        self.y = max(self.size, min(screen_height - self.size, self.y + dy * self.speed))

    def aim(self, angle):
        self.angle = angle

    def shoot(self, bullets):
        if self.fire_cooldown == 0:
            if self.current_weapon == "default":
                bullets.append(Bullet(self.x, self.y, self.angle, friendly=True))
                self.fire_cooldown = self.fire_rate
            elif self.current_weapon == "spread":
                for i in range(-1, 2):
                    bullets.append(Bullet(self.x, self.y, self.angle + i * 0.2, friendly=True))
                self.fire_cooldown = self.fire_rate * 2
            elif self.current_weapon == "laser":
                bullets.append(Bullet(self.x, self.y, self.angle, friendly=True, speed=20))
                self.fire_cooldown = self.fire_rate // 2
            elif self.current_weapon == "multishot":
                for _ in range(3):
                    bullets.append(Bullet(self.x, self.y, self.angle + random.uniform(-0.1, 0.1), friendly=True))
                self.fire_cooldown = self.fire_rate * 2
            elif self.current_weapon == "piercing":
                bullets.append(Bullet(self.x, self.y, self.angle, friendly=True, damage=3))
                self.fire_cooldown = self.fire_rate * 1.5

    def sword_attack(self):
        if self.sword_cooldown == 0:
            self.sword_cooldown = self.sword_cooldown_max
            return True
        return False

    def activate_shield(self):
        if not self.shield_active:
            self.shield_active = True
            self.shield_timer = 60  # Shield duration in frames

    def take_damage(self):
        if not self.shield_active:
            self.hits_remaining -= 1
            if self.hits_remaining <= 0:
                self.alive = False

    def update(self):
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        
        if self.sword_cooldown > 0:
            self.sword_cooldown -= 1

    def draw(self, screen):
        # Draw player triangle
        points = [
            (self.x + self.size * math.cos(self.angle), self.y + self.size * math.sin(self.angle)),
            (self.x + self.size * math.cos(self.angle + 2.5), self.y + self.size * math.sin(self.angle + 2.5)),
            (self.x + self.size * math.cos(self.angle - 2.5), self.y + self.size * math.sin(self.angle - 2.5))
        ]
        pygame.draw.polygon(screen, (255, 255, 255), points)

        # Draw hitbox indicator
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), self.hitbox_size, 1)

        # Draw shield if active
        if self.shield_active:
            pygame.draw.circle(screen, (0, 0, 255), (int(self.x), int(self.y)), self.size + 5, 2)

        # Draw sword attack if active
        if self.sword_cooldown > self.sword_cooldown_max // 2:
            end_x = self.x + self.sword_range * math.cos(self.angle)
            end_y = self.y + self.sword_range * math.sin(self.angle)
            pygame.draw.line(screen, (255, 255, 255), (self.x, self.y), (end_x, end_y), 2)

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.hitbox_size + other.size

    def is_on_screen(self, screen_width, screen_height):
        return self.size <= self.x < screen_width - self.size and self.size <= self.y < screen_height - self.size