import pygame
import math
import random
from player import Player
from enemy import Enemy
from bullet import Bullet
from powerup import PowerUp
from mechanics import GrazingSystem, PowerUpSystem, EnemyBehavior

class Game:
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)

    def __init__(self, screen, joystick):
        self.screen = screen
        self.joystick = joystick
        self.screen_width, self.screen_height = screen.get_size()
        self.player = Player(self.screen_width // 2, self.screen_height // 2)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.wave = 1
        self.graze_system = GrazingSystem()
        self.powerup_system = PowerUpSystem()
        self.enemy_behavior = EnemyBehavior()
        self.font = pygame.font.Font(None, 36)

    def reset(self):
        self.player = Player(self.screen_width // 2, self.screen_height // 2)
        self.bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.powerups = []
        self.score = 0
        self.wave = 1
        self.graze_system = GrazingSystem()
        self.spawn_enemies()

    def handle_input(self):
        if not self.player.alive:
            return

        # Movement (Left stick)
        move_x = self.joystick.get_axis(0)
        move_y = self.joystick.get_axis(1)
        self.player.move(move_x, move_y, self.screen_width, self.screen_height)

        # Aiming (Right stick)
        aim_x = self.joystick.get_axis(2)
        aim_y = self.joystick.get_axis(3)
        if abs(aim_x) > 0.1 or abs(aim_y) > 0.1:
            self.player.aim(math.atan2(aim_y, aim_x))

        # Shooting (Right trigger)
        if self.joystick.get_axis(5) > 0.5:
            self.player.shoot(self.bullets)

        # Sword attack (Right bumper)
        if self.joystick.get_button(5):
            if self.player.sword_attack():
                self.check_sword_collision()

        # Shield (Left bumper)
        if self.joystick.get_button(4):
            self.player.activate_shield()

    def update_game_state(self):
        if not self.player.alive:
            return

        self.player.update()
        self.update_bullets()
        self.update_enemies()
        self.update_powerups()
        self.check_collisions()
        self.graze_system.update(self.player, self.enemy_bullets, self.enemies)

        if len(self.enemies) == 0:
            self.wave += 1
            self.spawn_enemies()

    def update_bullets(self):
        for bullet in self.bullets[:]:
            if bullet.friendly and self.player.current_weapon == "homing":
                closest_enemy = min(self.enemies, key=lambda e: math.hypot(e.x - bullet.x, e.y - bullet.y), default=None)
                if closest_enemy:
                    dx = closest_enemy.x - bullet.x
                    dy = closest_enemy.y - bullet.y
                    angle = math.atan2(dy, dx)
                    bullet.angle = angle
            bullet.update()
            if not bullet.is_on_screen(self.screen_width, self.screen_height):
                self.bullets.remove(bullet)

        for bullet in self.enemy_bullets[:]:
            bullet.update()
            if not bullet.is_on_screen(self.screen_width, self.screen_height):
                self.enemy_bullets.remove(bullet)

    def update_enemies(self):
        for enemy in self.enemies[:]:
            self.enemy_behavior.update(enemy, self.player, self.enemy_bullets, self.score)

    def update_powerups(self):
        self.powerup_system.update(self.player, self.graze_system.level, self.wave)
        self.powerups = self.powerup_system.powerups

    def check_collisions(self):
        # Player bullets with enemies
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    enemy.take_damage(bullet.damage)
                    self.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.enemies.remove(enemy)
                        self.score += enemy.score_value
                    break

        # Enemy bullets with player
        for bullet in self.enemy_bullets[:]:
            if self.player.collides_with(bullet):
                if self.player.shield_active:
                    self.enemy_bullets.remove(bullet)
                else:
                    self.player.take_damage()
                    self.enemy_bullets.remove(bullet)

        # Player with enemies
        for enemy in self.enemies[:]:
            if self.player.collides_with(enemy):
                if not self.player.shield_active:
                    self.player.take_damage()

        # Player with powerups
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
                self.graze_system.add_meter(10)  # Add 10 to the graze meter for a successful sword hit
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.score += enemy.score_value

    def spawn_enemies(self):
        num_enemies = self.wave * 2
        for _ in range(num_enemies):
            enemy_type = self.enemy_behavior.get_enemy_type(self.graze_system.level)
            self.enemies.append(Enemy(enemy_type, self.screen_width, self.screen_height))

    def draw_game(self):
        self.screen.fill(self.BLACK)
        
        # Draw graze zones (only when active)
        self.graze_system.draw_graze_zones(self.screen, self.player)
        
        self.player.draw(self.screen)

        for bullet in self.bullets:
            bullet.draw(self.screen)

        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        for powerup in self.powerups:
            powerup.draw(self.screen)

        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw wave
        wave_text = self.font.render(f"Wave: {self.wave}", True, self.WHITE)
        self.screen.blit(wave_text, (10, 50))

        # Draw graze meter
        self.graze_system.draw(self.screen, self.screen_width)

        # Draw player health
        health_text = self.font.render(f"Health: {self.player.hits_remaining}", True, self.WHITE)
        self.screen.blit(health_text, (self.screen_width - 150, 10))

        # Draw current weapon
        weapon_text = self.font.render(f"Weapon: {self.player.current_weapon}", True, self.WHITE)
        self.screen.blit(weapon_text, (self.screen_width - 250, 50))

    def clear_screen(self):
        self.enemy_bullets.clear()
        for enemy in self.enemies:
            enemy.take_damage(enemy.health)  # Instantly defeat all enemies
        self.score += len(self.enemies) * 10  # Award points for cleared enemies
        self.enemies.clear()