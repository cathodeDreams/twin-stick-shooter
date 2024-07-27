import pygame
import math
import random
from player import Player
from enemy import Enemy
from bullet import Bullet
from powerup import PowerUp
from mechanics import GrazingSystem, PowerUpSystem, EnemyBehavior
from particle import Particle
from colors import Colors

class Game:
    def __init__(self, screen, joystick):
        self.screen = screen
        self.joystick = joystick
        self.screen_width, self.screen_height = screen.get_size()
        self.player = Player(self.screen_width // 2, self.screen_height // 2, self.screen_width, self.screen_height)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.wave = 1
        self.graze_system = GrazingSystem()
        self.powerup_system = PowerUpSystem(self)
        self.enemy_behavior = EnemyBehavior()
        self.font = pygame.font.Font(None, 36)
        
        # Create a slightly lighter background for the play area
        self.play_area_color = tuple(min(c + 10, 255) for c in Colors.BACKGROUND_COLOR)
        self.border_color = Colors.FOREGROUND
        self.border_width = 2

    def reset(self):
        self.player = Player(self.screen_width // 2, self.screen_height // 2, self.screen_width, self.screen_height)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.particles = []
        self.score = 0
        self.wave = 1
        self.graze_system = GrazingSystem()
        self.powerup_system.reset()
        self.spawn_enemies()

    def handle_input(self):
        if not self.player.alive:
            return

        move_x = self.joystick.get_axis(0)
        move_y = self.joystick.get_axis(1)
        self.player.move(move_x, move_y)

        aim_x = self.joystick.get_axis(2)
        aim_y = self.joystick.get_axis(3)
        if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
            self.player.aim(math.atan2(aim_y, aim_x))

        if self.joystick.get_axis(5) > 0.5:
            self.player.shoot(self.bullets)

        if self.joystick.get_button(5):
            if self.player.sword_attack():
                self.check_sword_collision()

        if self.joystick.get_button(4):
            self.player.activate_shield()

    def update_game_state(self):
        if not self.player.alive:
            return

        self.player.update()
        self.update_bullets()
        self.update_enemies()
        self.update_powerups()
        self.update_particles()
        self.check_collisions()
        self.graze_system.update(self.player, self.enemy_bullets, self.enemies)

        if self.graze_system.add_meter(0):  # Only level up if meter is full
            self.player.hits_remaining += 1

        if len(self.enemies) == 0:
            self.wave += 1
            self.spawn_enemies()

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet.bullet_type == "homing":
                closest_enemy = min(self.enemies, key=lambda e: math.hypot(e.x - bullet.x, e.y - bullet.y), default=None)
                bullet.update(closest_enemy)
            else:
                bullet.update()
            if not bullet.is_on_screen(self.screen_width, self.screen_height) or bullet.lifetime <= 0:
                self.bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.is_on_screen(self.screen_width, self.screen_height) or bullet.lifetime <= 0:
                self.enemy_bullets.remove(bullet)
                
    def update_enemies(self):
        for enemy in self.enemies[:]:
            self.enemy_behavior.update(enemy, self.player, self.enemy_bullets, self.score)

    def update_powerups(self):
        self.powerup_system.update(self.player, self.graze_system.level, self.wave)
        self.powerups = self.powerup_system.powerups

    def update_particles(self):
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

    def check_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    enemy.take_damage(bullet.damage)
                    if bullet.bullet_type != "piercing":
                        self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += enemy.score_value
                        self.add_particles(enemy.x, enemy.y)
                    break

        for bullet in self.enemy_bullets[:]:
            if self.player.collides_with(bullet):
                if self.player.shield_active:
                    self.enemy_bullets.remove(bullet)
                else:
                    self.player.take_damage()
                    self.enemy_bullets.remove(bullet)

        for enemy in self.enemies[:]:
            if self.player.collides_with(enemy):
                if not self.player.shield_active:
                    self.player.take_damage()

        for powerup in self.powerups[:]:
            if self.player.collides_with(powerup):
                self.powerup_system.activate_powerup(self.player, powerup.type)
                self.powerups.remove(powerup)

    def check_sword_collision(self):
        sword_rect = pygame.Rect(
            self.player.x - self.player.sword_range,
            self.player.y - self.player.sword_range,
            self.player.sword_range * 2,
            self.player.sword_range * 2
        )
        for enemy in self.enemies[:]:
            if sword_rect.collidepoint(enemy.x, enemy.y):
                enemy.take_damage(self.player.sword_damage)
                self.graze_system.add_meter(10)
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.score += enemy.score_value

    def spawn_enemies(self):
        num_enemies = self.wave * 2
        for _ in range(num_enemies):
            enemy_type = self.enemy_behavior.get_enemy_type(self.graze_system.level)
            self.enemies.append(Enemy(enemy_type, self.screen_width, self.screen_height))

    def draw_game(self):
        self.screen.fill(Colors.BACKGROUND_COLOR)
        
        # Draw the play area with a slightly lighter background
        pygame.draw.rect(self.screen, self.play_area_color, (0, 0, self.screen_width, self.screen_height))
        
        # Draw the border
        pygame.draw.rect(self.screen, self.border_color, (0, 0, self.screen_width, self.screen_height), self.border_width)
        
        self.graze_system.draw_graze_zones(self.screen, self.player)
        
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen, Colors.BOSS_COLOR, Colors.ENEMY_COLOR)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        for particle in self.particles:
            particle.draw(self.screen)

        self.draw_ui()

        pygame.display.flip()

    def update_game_state(self):
        if not self.player.alive:
            return

        self.player.update()
        self.update_bullets()
        self.update_enemies()
        self.update_powerups()
        self.update_particles()
        self.check_collisions()
        graze_level_up = self.graze_system.update(self.player, self.enemy_bullets, self.enemies)

        if graze_level_up:
            self.player.hits_remaining += 1

        if len(self.enemies) == 0:
            self.wave += 1
            self.spawn_enemies()

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, Colors.FOREGROUND)
        self.screen.blit(score_text, (10, 10))

        wave_text = self.font.render(f"Wave: {self.wave}", True, Colors.FOREGROUND)
        self.screen.blit(wave_text, (10, 50))

        self.graze_system.draw(self.screen, self.screen_width)

        health_text = self.font.render(f"Health: {self.player.hits_remaining}", True, Colors.FOREGROUND)
        self.screen.blit(health_text, (self.screen_width - 150, 10))

        weapon_text = self.font.render(f"Weapon: {self.player.current_weapon}", True, Colors.FOREGROUND)
        self.screen.blit(weapon_text, (self.screen_width // 2 - weapon_text.get_width() // 2, 10))

        if self.player.powerup_timer > 0:
            duration_text = self.font.render(f"Duration: {self.player.powerup_timer // 60 + 1}s", True, Colors.FOREGROUND)
            self.screen.blit(duration_text, (self.screen_width // 2 - duration_text.get_width() // 2, 50))

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

    def add_particles(self, x, y):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            lifetime = random.randint(30, 60)
            self.particles.append(Particle(x, y, angle, speed, lifetime))