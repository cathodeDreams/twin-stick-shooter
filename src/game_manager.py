import pygame
from enum import Enum

class GameState(Enum):
    RUNNING = 1
    PAUSED = 2
    GAME_OVER = 3

class GameManager:
    def __init__(self, screen, joystick, player, entity_manager, collision_manager, 
                 renderer, graze_system, powerup_system, enemy_behavior, arena_rect):
        self.screen = screen
        self.joystick = joystick
        self.player = player
        self.entity_manager = entity_manager
        self.collision_manager = collision_manager
        self.renderer = renderer
        self.graze_system = graze_system
        self.powerup_system = powerup_system
        self.enemy_behavior = enemy_behavior
        self.arena_rect = arena_rect
        self.state = GameState.RUNNING

    def reset(self):
        self.player.reset(self.screen.get_width() // 2, self.screen.get_height() // 2)
        self.entity_manager.reset()
        self.graze_system.reset()
        self.powerup_system.reset()
        self.entity_manager.spawn_enemies(1, self.enemy_behavior, self.graze_system.level)
        self.state = GameState.RUNNING

    def handle_input(self):
        if self.state != GameState.RUNNING:
            return

        self._handle_movement()
        self._handle_aiming()
        self._handle_shooting()
        self._handle_sword_attack()
        self._handle_shield()

    def _handle_movement(self):
        move_x = self.joystick.get_axis(0)
        move_y = self.joystick.get_axis(1)
        self.player.move(move_x, move_y)

    def _handle_aiming(self):
        aim_x = self.joystick.get_axis(2)
        aim_y = self.joystick.get_axis(3)
        self.player.aim(aim_x, aim_y)

    def _handle_shooting(self):
        if self.joystick.get_axis(5) > 0.5:
            self.player.shoot(self.entity_manager.bullets)

    def _handle_sword_attack(self):
        if self.joystick.get_button(5) and self.player.sword_attack():
            score = self.collision_manager.check_sword_collision(self.player, self.entity_manager.enemies, self.graze_system)
            self.entity_manager.add_score(score)

    def _handle_shield(self):
        if self.joystick.get_button(4):
            self.player.activate_shield()

    def update_game_state(self):
        if self.state != GameState.RUNNING:
            return

        self.player.update()
        self.entity_manager.update(self.player, self.enemy_behavior)
        self.powerup_system.update(self.player, self.graze_system.level, self.entity_manager.wave)
        self.entity_manager.powerups = self.powerup_system.powerups  # Update powerups in entity_manager
        self.graze_system.update(self.player, self.entity_manager.enemy_bullets, self.entity_manager.enemies)
        self.collision_manager.check_collisions(self.player, self.entity_manager, self.powerup_system, self.graze_system)

        if len(self.entity_manager.enemies) == 0:
            self._start_new_wave()

        if not self.player.alive:
            self.state = GameState.GAME_OVER

        if self.player.sword_active:
            sword_hits = self.collision_manager.check_sword_collision(self.player, self.entity_manager.enemies, self.graze_system)
            self.entity_manager.add_score(sword_hits * 10)  # 10 points per sword hit
            
    def _start_new_wave(self):
        self.entity_manager.wave += 1
        self.entity_manager.spawn_enemies(self.entity_manager.wave, self.enemy_behavior, self.graze_system.level)
        print(f"Starting wave {self.entity_manager.wave}")  # Debug print

    def draw_game(self):
        self.renderer.draw_game(self.player, self.entity_manager, self.graze_system)
        pygame.display.flip()

    def activate_bomb(self):
        self.entity_manager.activate_bomb()

    def clear_screen(self):
        self.entity_manager.clear_screen()

    def toggle_pause(self):
        if self.state == GameState.RUNNING:
            self.state = GameState.PAUSED
        elif self.state == GameState.PAUSED:
            self.state = GameState.RUNNING

    @property
    def score(self):
        return self.entity_manager.score

    @property
    def is_game_over(self):
        return self.state == GameState.GAME_OVER

    @property
    def is_paused(self):
        return self.state == GameState.PAUSED