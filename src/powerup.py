import pygame
import math
from colors import Colors
from effects import apply_glow_and_shadow

class PowerUp:
    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.size = 20
        self.type = powerup_type
        self.pulsate_timer = 0

    def draw(self, screen):
        color = self.get_color()
        apply_glow_and_shadow(screen, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        
        # Draw an icon or letter to represent the powerup type
        font = pygame.font.Font(None, 20)
        text = font.render(self.get_icon(), True, Colors.BACKGROUND)
        text_rect = text.get_rect(center=(self.x, self.y))
        screen.blit(text, text_rect)

        # Pulsating effect
        self.pulsate_timer += 0.1
        pulse = int(math.sin(self.pulsate_timer) * 3)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size + pulse, 2)

    def get_color(self):
        return Colors.POWERUP_COLORS.get(self.type, Colors.FOREGROUND)

    def get_icon(self):
        icons = {
            "spread": "S",
            "laser": "L",
            "homing": "H",
            "multishot": "M",
            "shield": "D",
            "bomb": "B",
            "piercing": "P"
        }
        return icons.get(self.type, "?")

    def collides_with(self, other):
        return math.hypot(self.x - other.x, self.y - other.y) < self.size + other.size

    def is_on_screen(self, screen_width, screen_height):
        return 0 <= self.x < screen_width and 0 <= self.y < screen_height