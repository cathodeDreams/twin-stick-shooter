import pygame
from colors import Colors
from effects import apply_glow_and_shadow

class Renderer:
    def __init__(self, screen, arena_rect):
        self.screen = screen
        self.arena_rect = arena_rect
        self.play_area_color = tuple(min(c + 10, 255) for c in Colors.BACKGROUND_COLOR)
        self.border_color = Colors.FOREGROUND
        self.font = pygame.font.Font(None, 24)

    def draw_game(self, player, entity_manager, graze_system):
        self.screen.fill(Colors.BACKGROUND_COLOR)
        
        # Draw the play area with a slightly lighter background
        pygame.draw.rect(self.screen, self.play_area_color, self.arena_rect)
        
        # Draw the border
        pygame.draw.rect(self.screen, self.border_color, self.arena_rect, 2)
        
        graze_system.draw_graze_zones(self.screen, player)
        
        for bullet in entity_manager.bullets:
            apply_glow_and_shadow(self.screen, Colors.BULLET_COLOR, (int(bullet.x), int(bullet.y)), bullet.size)
            bullet.draw(self.screen)

        for bullet in entity_manager.enemy_bullets:
            apply_glow_and_shadow(self.screen, Colors.ENEMY_COLOR, (int(bullet.x), int(bullet.y)), bullet.size)
            bullet.draw(self.screen)

        for enemy in entity_manager.enemies:
            enemy.draw(self.screen, Colors.BOSS_COLOR, Colors.ENEMY_COLOR)

        for powerup in entity_manager.powerups:
            apply_glow_and_shadow(self.screen, powerup.get_color(), (int(powerup.x), int(powerup.y)), powerup.size)
            powerup.draw(self.screen)

        for particle in entity_manager.particles:
            apply_glow_and_shadow(self.screen, particle.color, (int(particle.x), int(particle.y)), particle.size, glow_intensity=0.3)
            particle.draw(self.screen)

        player.draw(self.screen)

        self.draw_ui(player, entity_manager, graze_system)

    def draw_ui(self, player, entity_manager, graze_system):
        ui_y = self.arena_rect.top - 30  # Position UI elements 30 pixels above the arena border
        
        # Draw score
        score_text = self.font.render(f"Score: {entity_manager.score}", True, Colors.FOREGROUND)
        self.screen.blit(score_text, (self.arena_rect.left, ui_y))
        
        # Draw wave
        wave_text = self.font.render(f"Wave: {entity_manager.wave}", True, Colors.FOREGROUND)
        wave_x = self.arena_rect.left + score_text.get_width() + 20
        self.screen.blit(wave_text, (wave_x, ui_y))
        
        # Draw weapon
        weapon_text = self.font.render(f"Weapon: {player.current_weapon}", True, Colors.FOREGROUND)
        weapon_x = self.arena_rect.centerx - weapon_text.get_width() // 2
        self.screen.blit(weapon_text, (weapon_x, ui_y))
        
        # Draw graze meter
        graze_meter_width = 100
        graze_meter_height = 10
        graze_meter_x = self.arena_rect.right - graze_meter_width - 100
        pygame.draw.rect(self.screen, Colors.COMMENT, (graze_meter_x, ui_y + 7, graze_meter_width, graze_meter_height))
        fill_width = int(graze_system.meter / graze_system.max_meter * graze_meter_width)
        pygame.draw.rect(self.screen, Colors.PURPLE, (graze_meter_x, ui_y + 7, fill_width, graze_meter_height))
        
        # Draw graze level
        graze_text = self.font.render(f"Graze: {graze_system.level}", True, Colors.FOREGROUND)
        graze_x = graze_meter_x - graze_text.get_width() - 10
        self.screen.blit(graze_text, (graze_x, ui_y))
        
        # Draw health
        health_text = self.font.render(f"Health: {player.hits_remaining}", True, Colors.FOREGROUND)
        health_x = self.arena_rect.right - health_text.get_width()
        self.screen.blit(health_text, (health_x, ui_y))