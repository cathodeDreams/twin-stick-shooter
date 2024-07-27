import math
import random
from enemy import Enemy
from particle import Particle

class EntityManager:
    def __init__(self, arena_rect):
        self.arena_rect = arena_rect
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.wave = 1

    def reset(self):
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.enemies.clear()
        self.powerups.clear()
        self.particles.clear()
        self.score = 0
        self.wave = 1

    def update(self, player, enemy_behavior):
        self.update_bullets()
        self.update_enemies(player, enemy_behavior)
        self.update_particles()
        self.update_powerups()  # Add this line to update powerups

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet.bullet_type == "homing":
                closest_enemy = min(self.enemies, key=lambda e: math.hypot(e.x - bullet.x, e.y - bullet.y), default=None)
                bullet.update(self.arena_rect, closest_enemy)
            else:
                bullet.update(self.arena_rect)
            if not bullet.is_on_screen(self.arena_rect) or bullet.lifetime <= 0:
                self.bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update(self.arena_rect)
            if not bullet.is_on_screen(self.arena_rect) or bullet.lifetime <= 0:
                self.enemy_bullets.remove(bullet)

    def update_enemies(self, player, enemy_behavior):
        for enemy in self.enemies[:]:
            enemy_behavior.update(enemy, player, self.enemy_bullets, self.score)

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def update_powerups(self):
        for powerup in self.powerups[:]:
            if not powerup.is_on_screen(self.arena_rect.width, self.arena_rect.height):
                self.powerups.remove(powerup)
                print(f"Removed powerup at ({powerup.x}, {powerup.y})")  # Debug print

    def spawn_enemies(self, wave, enemy_behavior, graze_level):
        num_enemies = int(math.ceil(2 * math.exp(0.2 * wave)))  # Exponential growth
        for _ in range(num_enemies):
            enemy_type = enemy_behavior.get_enemy_type(graze_level)
            self.enemies.append(Enemy(enemy_type, self.arena_rect))

    def add_particles(self, x, y):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            lifetime = random.randint(30, 60)
            self.particles.append(Particle(x, y, angle, speed, lifetime))

    def activate_bomb(self):
        for enemy in self.enemies[:]:
            enemy.take_damage(10)
            if enemy.health <= 0:
                self.enemies.remove(enemy)
                self.score += enemy.score_value
        self.enemy_bullets.clear()

    def clear_screen(self):
        self.enemy_bullets.clear()
        for enemy in self.enemies:
            enemy.take_damage(enemy.health)
        self.score += len(self.enemies) * 10
        self.enemies.clear()

    def add_score(self, points):
        self.score += points