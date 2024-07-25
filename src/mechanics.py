import random
import math
import pygame
from bullet import Bullet
from powerup import PowerUp

class GrazingSystem:
    def __init__(self):
        self.meter = 0
        self.level = 0
        self.max_meter = 100
        self.outer_graze_distance = 60
        self.inner_graze_distance = 30
        self.font = pygame.font.Font(None, 24)
        self.graze_rings = []
        self.ring_fade_time = 30  # Frames for a ring to fade out

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

    def level_up(self):
        self.level += 1
        self.meter = 0

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
        y = 50
        pygame.draw.rect(screen, (100, 100, 100), (x, y, meter_width, meter_height))
        fill_width = int(self.meter / self.max_meter * meter_width)
        pygame.draw.rect(screen, (0, 0, 255), (x, y, fill_width, meter_height))
        
        # Draw graze level
        level_text = self.font.render(f"Graze Level: {self.level}", True, (255, 255, 255))
        screen.blit(level_text, (x, y + meter_height + 5))

    def draw_graze_zones(self, screen, player):
        for ring in self.graze_rings:
            color = (255, 0, 0) if ring['zone'] == 'red' else (0, 0, 255)
            alpha = int(255 * (ring['time'] / self.ring_fade_time))
            surface = pygame.Surface((self.outer_graze_distance * 2, self.outer_graze_distance * 2), pygame.SRCALPHA)
            pygame.draw.arc(surface, (*color, alpha),
                            (0, 0, self.outer_graze_distance * 2, self.outer_graze_distance * 2),
                            ring['angle'] - 0.3, ring['angle'] + 0.3, 3)
            screen.blit(surface, (ring['x'] - self.outer_graze_distance, ring['y'] - self.outer_graze_distance))

class PowerUpSystem:
    def __init__(self):
        self.powerups = []
        self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb", "piercing"]
        self.powerup_duration = 600  # 10 seconds at 60 FPS
        self.wave_number = 1
        self.max_powerups = 3

    def update(self, player, graze_level, wave):
        self.wave_number = wave
        self.spawn_powerups()
        self.update_player_powerup(player)

    def spawn_powerups(self):
        if self.wave_number >= 2 and self.wave_number % 2 == 0 and len(self.powerups) < self.max_powerups:
            if random.random() < 0.1:  # 10% chance to spawn a powerup on even waves
                x = random.randint(50, 750)  # Assuming screen width of 800
                y = random.randint(50, 550)  # Assuming screen height of 600
                powerup_type = random.choice(self.available_powerups)
                self.powerups.append(PowerUp(x, y, powerup_type))
                self.available_powerups.remove(powerup_type)

    def activate_powerup(self, player, powerup_type):
        player.current_weapon = powerup_type
        player.powerup_timer = self.powerup_duration
        if powerup_type == "shield":
            player.activate_shield()
        elif powerup_type == "bomb":
            # This should be handled in the Game class
            pass

    def update_player_powerup(self, player):
        if player.powerup_timer > 0:
            player.powerup_timer -= 1
            if player.powerup_timer <= 0:
                player.current_weapon = "default"
                # Return the powerup type to available powerups
                if player.current_weapon != "default":
                    self.available_powerups.append(player.current_weapon)

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
        elif enemy.type == "boss":
            self.boss_behavior(enemy, player, enemy_bullets)

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

    def boss_behavior(self, enemy, player, enemy_bullets):
        enemy.x = 400 + math.sin(pygame.time.get_ticks() * 0.001 * self.difficulty_multiplier) * 200
        enemy.y = min(enemy.y + 0.5 * self.difficulty_multiplier, 150)

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
            return "normal"
        elif graze_level < 6:
            return random.choice(["normal", "fast"])
        else:
            choices = ["normal", "fast", "tough"]
            weights = [1, 1 + self.difficulty_multiplier * 0.5, self.difficulty_multiplier - 1]
            return random.choices(choices, weights=weights)[0]