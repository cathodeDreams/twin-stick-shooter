import pygame
import math
import random
from bullet import Bullet
from colors import Colors

class Player:
    def __init__(self, x, y, screen_width, screen_height):
        self.x = x
        self.y = y
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.size = 20
        self.hitbox_size = 5
        self.speed = 5
        self.angle = 0
        self.alive = True
        self.shield_active = False
        self.shield_timer = 0
        self.hits_remaining = 1
        self.current_weapon = "default"
        self.fire_cooldown = 0
        self.fire_rate = 15
        self.sword_cooldown = 0
        self.sword_cooldown_max = 30
        self.sword_range = 50
        self.sword_damage = 5
        self.powerup_timer = 0
        self.kickback_timer = 0
        self.glow_timer = 0

    def move(self, dx, dy):
        if self.kickback_timer > 0:
            self.x -= dx * self.speed * 0.5
            self.y -= dy * self.speed * 0.5
            self.kickback_timer -= 1
        self.x = max(self.size, min(self.screen_width - self.size, self.x + dx * self.speed))
        self.y = max(self.size, min(self.screen_height - self.size, self.y + dy * self.speed))

    def aim(self, angle):
        self.angle = angle

    def shoot(self, bullets):
        if self.fire_cooldown == 0:
            if self.current_weapon == "default":
                bullet = Bullet(self.x, self.y, self.angle, friendly=True)
                bullet.start_glow()
                bullets.append(bullet)
                self.fire_cooldown = self.fire_rate
                self.kickback_timer = 5
            elif self.current_weapon == "spread":
                for i in range(-1, 2):
                    bullet = Bullet(self.x, self.y, self.angle + i * 0.2, friendly=True)
                    bullet.start_glow()
                    bullets.append(bullet)
                self.fire_cooldown = self.fire_rate * 2
                self.kickback_timer = 8
            elif self.current_weapon == "laser":
                bullet = Bullet(self.x, self.y, self.angle, friendly=True, speed=20, bullet_type="laser")
                bullet.start_glow()
                bullets.append(bullet)
                self.fire_cooldown = self.fire_rate // 2
                self.kickback_timer = 3
            elif self.current_weapon == "homing":
                bullet = Bullet(self.x, self.y, self.angle, friendly=True, speed=5, bullet_type="homing")
                bullet.start_glow()
                bullets.append(bullet)
                self.fire_cooldown = self.fire_rate
                self.kickback_timer = 5
            elif self.current_weapon == "multishot":
                for _ in range(3):
                    bullet = Bullet(self.x, self.y, self.angle + random.uniform(-0.1, 0.1), friendly=True)
                    bullet.start_glow()
                    bullets.append(bullet)
                self.fire_cooldown = self.fire_rate * 2
                self.kickback_timer = 8

    def sword_attack(self):
        if self.sword_cooldown == 0:
            self.sword_cooldown = self.sword_cooldown_max
            return True
        return False

    def activate_shield(self):
        if not self.shield_active:
            self.shield_active = True
            self.shield_timer = 60

    def take_damage(self):
        if not self.shield_active:
            self.hits_remaining -= 1
            if self.hits_remaining <= 0:
                self.alive = False
            self.glow_timer = 30

    def update(self):
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False
        
        if self.fire_cooldown > 0:
            self.fire_cooldown -= 1
        
        if self.sword_cooldown > 0:
            self.sword_cooldown -= 1

        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.current_weapon = "default"

        if self.glow_timer > 0:
            self.glow_timer -= 1

    def draw(self, screen):
        # Draw player triangle
        points = [
            (self.x + self.size * math.cos(self.angle), self.y + self.size * math.sin(self.angle)),
            (self.x + self.size * math.cos(self.angle + 2.5), self.y + self.size * math.sin(self.angle + 2.5)),
            (self.x + self.size * math.cos(self.angle - 2.5), self.y + self.size * math.sin(self.angle - 2.5))
        ]
        pygame.draw.polygon(screen, Colors.PLAYER_COLOR, points)

        # Draw hitbox indicator
        pygame.draw.circle(screen, Colors.RED, (int(self.x), int(self.y)), self.hitbox_size, 1)

        # Draw shield if active
        if self.shield_active:
            pygame.draw.circle(screen, Colors.SHIELD_COLOR, (int(self.x), int(self.y)), self.size + 5, 2)

        # Draw sword attack if active
        if self.sword_cooldown > self.sword_cooldown_max // 2:
            end_x = self.x + self.sword_range * math.cos(self.angle)
            end_y = self.y + self.sword_range * math.sin(self.angle)
            pygame.draw.line(screen, Colors.PLAYER_COLOR, (self.x, self.y), (end_x, end_y), 2)

        if self.glow_timer > 0:
            glow_color = Colors.PLAYER_COLOR
            glow_size = self.size + self.glow_timer // 5
            glow_alpha = 128 * (self.glow_timer / 30)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*glow_color, int(glow_alpha)), (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.hitbox_size + other.size

    def is_on_screen(self, screen_width, screen_height):
        return self.size <= self.x < screen_width - self.size and self.size <= self.y < screen_height - self.size