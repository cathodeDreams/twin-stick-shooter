import pygame
import math
from colors import Colors

class GrazingSystem:
    def __init__(self):
        self.reset()
        self.max_meter = 100
        self.outer_graze_distance = 60
        self.inner_graze_distance = 30
        self.font = pygame.font.Font(None, 24)
        self.ring_fade_time = 30

    def reset(self):
        self.meter = 0
        self.level = 0
        self.graze_rings = []

    def update(self, player, enemy_bullets, enemies):
        self.update_graze_rings()
        for bullet in enemy_bullets:
            self.check_graze(player, bullet)
        for enemy in enemies:
            self.check_graze(player, enemy)
        
        if self.meter >= self.max_meter:
            self.level_up(player)
            return True
        return False

    def check_graze(self, player, entity):
        distance = math.hypot(entity.x - player.x, entity.y - player.y)
        if player.hitbox_size < distance <= self.outer_graze_distance:
            if distance <= self.inner_graze_distance:
                self.add_meter(2)  # Fast fill for red zone
                self.add_graze_ring(player, entity, 'red')
            else:
                self.add_meter(0.5)  # Slower fill for blue zone
                self.add_graze_ring(player, entity, 'blue')

    def add_meter(self, amount):
        self.meter += amount
        self.meter = min(self.meter, self.max_meter)

    def level_up(self, player):
        self.level += 1
        self.meter = 0
        player.hits_remaining += 1
        print(f"Graze level up! New level: {self.level}, Player health: {player.hits_remaining}")

    def add_graze_ring(self, player, entity, zone):
        angle = math.atan2(entity.y - player.y, entity.x - player.x)
        self.graze_rings.append({
            'x': player.x,
            'y': player.y,
            'angle': angle,
            'zone': zone,
            'time': self.ring_fade_time
        })

    def update_graze_rings(self):
        for ring in self.graze_rings[:]:
            ring['time'] -= 1
            if ring['time'] <= 0:
                self.graze_rings.remove(ring)

    def draw(self, screen, screen_width):
        # Draw graze meter
        meter_width = 200
        meter_height = 20
        x = screen_width - meter_width - 10
        y = 10
        pygame.draw.rect(screen, Colors.COMMENT, (x, y, meter_width, meter_height))
        fill_width = int(self.meter / self.max_meter * meter_width)
        pygame.draw.rect(screen, Colors.PURPLE, (x, y, fill_width, meter_height))
        
        # Draw graze level
        level_text = self.font.render(f"Graze Level: {self.level}", True, Colors.FOREGROUND)
        screen.blit(level_text, (x - level_text.get_width() - 10, y + 5))

    def draw_graze_zones(self, screen, player):
        for ring in self.graze_rings:
            color = Colors.GRAZE_INNER_COLOR if ring['zone'] == 'red' else Colors.GRAZE_OUTER_COLOR
            alpha = int(255 * (ring['time'] / self.ring_fade_time))
            surface = pygame.Surface((self.outer_graze_distance * 2, self.outer_graze_distance * 2), pygame.SRCALPHA)
            pygame.draw.arc(surface, (*color, alpha),
                            (0, 0, self.outer_graze_distance * 2, self.outer_graze_distance * 2),
                            ring['angle'] - 0.3, ring['angle'] + 0.3, 3)
            screen.blit(surface, (ring['x'] - self.outer_graze_distance, ring['y'] - self.outer_graze_distance))