import random
import math
import pygame
from bullet import Bullet
from powerup import PowerUp
from colors import Colors

class GrazingSystem:
    def __init__(self):
        self.meter = 0
        self.level = 0
        self.max_meter = 100
        self.outer_graze_distance = 60
        self.inner_graze_distance = 30
        self.font = pygame.font.Font(None, 24)
        self.graze_rings = []
        self.ring_fade_time = 30

    def update(self, player, enemy_bullets, enemies):
        self.update_graze_rings()
        for bullet in enemy_bullets:
            self.check_graze(player, bullet)
        for enemy in enemies:
            self.check_graze(player, enemy)

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
        if self.meter >= self.max_meter:
            self.level_up()
            return True
        return False

    def level_up(self):
        self.level += 1
        self.meter = 0
        return True

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

class PowerUpSystem:
    def __init__(self, game):
        self.game = game
        self.powerups = []
        self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb"]
        self.powerup_duration = 600  # 10 seconds at 60 FPS
        self.wave_number = 1
        self.max_powerups = 3

    def reset(self):
        self.powerups = []
        self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb"]

    def update(self, player, graze_level, wave):
        self.wave_number = wave
        self.spawn_powerups()
        self.update_player_powerup(player)

    def spawn_powerups(self):
        if self.wave_number >= 2 and self.wave_number % 2 == 0 and len(self.powerups) < self.max_powerups:
            if random.random() < 0.1:
                x = random.randint(50, self.game.screen_width - 50)
                y = random.randint(50, self.game.screen_height - 50)
            
                if not self.available_powerups:
                    self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb"]
            
                powerup_type = random.choice(self.available_powerups)
                self.powerups.append(PowerUp(x, y, powerup_type))
                self.available_powerups.remove(powerup_type)

    def activate_powerup(self, player, powerup_type):
        player.current_weapon = powerup_type
        player.powerup_timer = self.powerup_duration
        if powerup_type == "shield":
            player.activate_shield()
        elif powerup_type == "bomb":
            self.game.activate_bomb()

    def update_player_powerup(self, player):
        if player.powerup_timer > 0:
            player.powerup_timer -= 1
            if player.powerup_timer <= 0:
                player.current_weapon = "default"
                
class EnemyBehavior:
    def __init__(self):
        self.base_enemy_fire_rate = 60
        self.difficulty_multiplier = 1.0

    def update_difficulty(self, score):
        # Increase difficulty based on score
        self.difficulty_multiplier = 1.0 + (score // 1000) * 0.1
        # Cap the difficulty multiplier at 2.0
        self.difficulty_multiplier = min(self.difficulty_multiplier, 2.0)

    def update(self, enemy, player, enemy_bullets, score):
        self.update_difficulty(score)
        
        if enemy.type == "normal":
            self.normal_enemy_behavior(enemy, player, enemy_bullets)
        elif enemy.type == "fast":
            self.fast_enemy_behavior(enemy, player, enemy_bullets)
        elif enemy.type == "tough":
            self.tough_enemy_behavior(enemy, player, enemy_bullets)
        elif enemy.type == "flanker":
            self.flanker_behavior(enemy, player, enemy_bullets)
        elif enemy.type == "zigzag":
            self.zigzag_behavior(enemy, player, enemy_bullets)
        elif enemy.type == "boss":
            self.boss_behavior(enemy, player, enemy_bullets)

        # Keep enemies within arena bounds
        enemy.x = max(enemy.arena_rect.left + enemy.size, min(enemy.arena_rect.right - enemy.size, enemy.x))
        enemy.y = max(enemy.arena_rect.top + enemy.size, min(enemy.arena_rect.bottom - enemy.size, enemy.y))

    def normal_enemy_behavior(self, enemy, player, enemy_bullets):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            speed = 2 * self.difficulty_multiplier
            enemy.x += dx / dist * speed
            enemy.y += dy / dist * speed

        if random.randint(1, int(self.base_enemy_fire_rate / self.difficulty_multiplier)) == 1:
            self.enemy_shoot(enemy, player, enemy_bullets)

    def fast_enemy_behavior(self, enemy, player, enemy_bullets):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            speed = 3 * self.difficulty_multiplier
            enemy.x += dx / dist * speed + random.uniform(-1, 1)
            enemy.y += dy / dist * speed + random.uniform(-1, 1)

        if random.randint(1, int(self.base_enemy_fire_rate / 2 / self.difficulty_multiplier)) == 1:
            self.enemy_shoot(enemy, player, enemy_bullets)

    def tough_enemy_behavior(self, enemy, player, enemy_bullets):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        if dist != 0:
            speed = 1.5 * self.difficulty_multiplier
            enemy.x += dx / dist * speed
            enemy.y += dy / dist * speed

        if random.randint(1, int(self.base_enemy_fire_rate / self.difficulty_multiplier)) == 1:
            angle = math.atan2(dy, dx)
            spread = 3 + int(self.difficulty_multiplier)
            for i in range(-spread // 2, spread // 2 + 1):
                self.enemy_shoot(enemy, player, enemy_bullets, angle + i * 0.2)

    def flanker_behavior(self, enemy, player, enemy_bullets):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)
        
        if dist > 200:
            # Approach the player from the sides
            speed = 2 * self.difficulty_multiplier
            angle = math.atan2(dy, dx) + math.pi / 2  # Perpendicular to the player's direction
            enemy.x += math.cos(angle) * speed
            enemy.y += math.sin(angle) * speed
        else:
            # Circle around the player
            speed = 2 * self.difficulty_multiplier
            angle = math.atan2(dy, dx)
            enemy.x += math.cos(angle + math.pi / 2) * speed
            enemy.y += math.sin(angle + math.pi / 2) * speed

        if random.randint(1, int(self.base_enemy_fire_rate / self.difficulty_multiplier)) == 1:
            self.enemy_shoot(enemy, player, enemy_bullets)

    def zigzag_behavior(self, enemy, player, enemy_bullets):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        dist = math.hypot(dx, dy)

        if dist != 0:
            speed = 2 * self.difficulty_multiplier
            angle = math.atan2(dy, dx)
            enemy.x += math.cos(angle) * speed
            enemy.y += math.sin(angle) * speed

            # Zigzag movement
            enemy.x += math.cos(enemy.y / 30) * speed
            enemy.y += math.sin(enemy.x / 30) * speed

        if random.randint(1, int(self.base_enemy_fire_rate / self.difficulty_multiplier)) == 1:
            self.enemy_shoot(enemy, player, enemy_bullets)

    def boss_behavior(self, enemy, player, enemy_bullets):
        enemy.x = enemy.arena_rect.left + enemy.arena_rect.width // 2 + math.sin(pygame.time.get_ticks() * 0.001 * self.difficulty_multiplier) * (enemy.arena_rect.width // 4)
        enemy.y = min(enemy.y + 0.5 * self.difficulty_multiplier, enemy.arena_rect.top + 150)

        time = pygame.time.get_ticks() * 0.001
        if int(time * 2 * self.difficulty_multiplier) % 2 == 0:
            self.boss_spiral_shot(enemy, enemy_bullets)
        else:
            self.boss_aimed_shot(enemy, player, enemy_bullets)

    def boss_spiral_shot(self, enemy, enemy_bullets):
        num_bullets = int(8 * self.difficulty_multiplier)
        for i in range(num_bullets):
            angle = (pygame.time.get_ticks() * 0.01 * self.difficulty_multiplier + i * (2 * math.pi / num_bullets)) % (2 * math.pi)
            self.enemy_shoot(enemy, None, enemy_bullets, angle)

    def boss_aimed_shot(self, enemy, player, enemy_bullets):
        dx = player.x - enemy.x
        dy = player.y - enemy.y
        angle = math.atan2(dy, dx)
        spread = 5 + int(self.difficulty_multiplier)
        for i in range(-spread // 2, spread // 2 + 1):
            self.enemy_shoot(enemy, None, enemy_bullets, angle + i * 0.2)

    def enemy_shoot(self, enemy, player, enemy_bullets, angle=None):
        if angle is None:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            angle = math.atan2(dy, dx)
        bullet_speed = 5 * self.difficulty_multiplier
        enemy_bullets.append(Bullet(enemy.x, enemy.y, angle, friendly=False, speed=bullet_speed))

    def get_enemy_type(self, graze_level):
        if graze_level < 3:
            return random.choice(["normal", "fast", "flanker", "zigzag"])
        elif graze_level < 6:
            return random.choice(["normal", "fast", "tough", "flanker", "zigzag"])
        else:
            choices = ["normal", "fast", "tough", "flanker", "zigzag"]
            weights = [1, 1 + self.difficulty_multiplier * 0.5, self.difficulty_multiplier - 1, 1, 1]
            return random.choices(choices, weights=weights)[0]