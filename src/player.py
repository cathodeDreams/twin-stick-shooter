import pygame
import math
import random
from bullet import Bullet
from colors import Colors
from effects import apply_glow_and_shadow

class Player:
    def __init__(self, x, y, arena_rect):
        self.arena_rect = arena_rect
        self.reset(x, y)

    def reset(self, x, y):
        self.x = x
        self.y = y
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
        self.sword_cooldown_max = 30  # Half a second at 60 FPS
        self.sword_active = False
        self.sword_active_time = 0
        self.sword_active_max = 10  # About 1/6 second at 60 FPS
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
        new_x = max(self.arena_rect.left + self.size, min(self.arena_rect.right - self.size, self.x + dx * self.speed))
        new_y = max(self.arena_rect.top + self.size, min(self.arena_rect.bottom - self.size, self.y + dy * self.speed))
        self.x, self.y = new_x, new_y

    def aim(self, aim_x, aim_y):
        if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
            self.angle = math.atan2(aim_y, aim_x)

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
            self.sword_active = True
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
        if self.sword_active:
            self.sword_active_time += 1
            if self.sword_active_time >= self.sword_active_max:
                self.sword_active = False
                self.sword_active_time = 0

        if self.powerup_timer > 0:
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                self.current_weapon = "default"

        if self.glow_timer > 0:
            self.glow_timer -= 1

    def draw(self, screen):
        apply_glow_and_shadow(screen, Colors.PLAYER_COLOR, (int(self.x), int(self.y)), self.size)
        
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

        if self.sword_active:
            sword_length = self.size * 2
            end_x = self.x + sword_length * math.cos(self.angle)
            end_y = self.y + sword_length * math.sin(self.angle)
            pygame.draw.line(screen, Colors.CYAN, (self.x, self.y), (end_x, end_y), 3)

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