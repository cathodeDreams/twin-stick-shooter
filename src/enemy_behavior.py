import random
import math
import pygame
from bullet import Bullet
from typing import Optional

class EnemyBehavior:
    def __init__(self):
        self.base_enemy_fire_rate = 60
        self.difficulty_multiplier = 1.0

    def update_difficulty(self, score: int) -> None:
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

    def enemy_shoot(self, enemy, player, enemy_bullets: list, angle: Optional[float] = None) -> None:
        if angle is None and player is not None:
            dx = player.x - enemy.x
            dy = player.y - enemy.y
            angle = math.atan2(dy, dx)
        elif angle is None:
            angle = 0  # Default angle if both angle and player are None
        bullet_speed = 5 * self.difficulty_multiplier
        enemy_bullets.append(Bullet(enemy.x, enemy.y, angle, friendly=False, speed=bullet_speed))

    def get_enemy_type(self, graze_level):
        if graze_level < 3:
            return random.choice(["normal", "fast"])
        elif graze_level < 6:
            return random.choice(["normal", "fast", "tough"])
        else:
            return random.choice(["normal", "fast", "tough", "flanker", "zigzag"])