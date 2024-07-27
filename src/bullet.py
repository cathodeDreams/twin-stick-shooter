import pygame
import math
from colors import Colors

class Bullet:
    def __init__(self, x, y, angle, friendly=False, speed=10, damage=1, bullet_type="default"):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.size = 3
        self.friendly = friendly
        self.damage = damage
        self.bullet_type = bullet_type
        self.lifetime = 180  # 3 seconds at 60 FPS
        self.target = None  # For homing bullets
        self.glow_timer = 0  # Timer for glowing effect

    def update(self, target=None):
        if self.bullet_type == "homing" and target:
            self.home_in_on_target(target)
        else:
            self.x += self.speed * math.cos(self.angle)
            self.y += self.speed * math.sin(self.angle)
        self.lifetime -= 1

        # Update glow timer
        if self.glow_timer > 0:
            self.glow_timer -= 1

    def home_in_on_target(self, target):
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            self.angle = math.atan2(dy, dx)
        self.x += self.speed * math.cos(self.angle)
        self.y += self.speed * math.sin(self.angle)

    def draw(self, screen):
        color = Colors.BULLET_COLOR if self.friendly else Colors.ENEMY_COLOR
        if self.bullet_type == "laser":
            pygame.draw.line(screen, color, (int(self.x), int(self.y)), 
                             (int(self.x + self.speed * 2 * math.cos(self.angle)), 
                              int(self.y + self.speed * 2 * math.sin(self.angle))), 2)
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

        # Draw glowing effect
        if self.glow_timer > 0:
            glow_color = Colors.BULLET_COLOR if self.friendly else Colors.ENEMY_COLOR
            glow_size = self.size + self.glow_timer // 5
            glow_alpha = 128 * (self.glow_timer / 30)
            glow_surface = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*glow_color, int(glow_alpha)), (glow_size, glow_size), glow_size)
            screen.blit(glow_surface, (int(self.x - glow_size), int(self.y - glow_size)))

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.size + other.size

    def is_on_screen(self, screen_width, screen_height):
        return 0 <= self.x < screen_width and 0 <= self.y < screen_height

    def start_glow(self):
        self.glow_timer = 30  # Glow for 0.5 seconds