import pygame

class CollisionManager:
    def check_collisions(self, player, entity_manager, powerup_system, graze_system):
        self.check_bullet_enemy_collisions(entity_manager)
        self.check_enemy_bullet_player_collisions(player, entity_manager)
        self.check_enemy_player_collisions(player, entity_manager.enemies)
        self.check_powerup_player_collisions(player, entity_manager.powerups, powerup_system)

    def check_bullet_enemy_collisions(self, entity_manager):
        for bullet in entity_manager.bullets[:]:
            for enemy in entity_manager.enemies[:]:
                if bullet.collides_with(enemy):
                    enemy.take_damage(bullet.damage)
                    if bullet.bullet_type != "piercing":
                        entity_manager.bullets.remove(bullet)
                    if enemy.health <= 0:
                        entity_manager.enemies.remove(enemy)
                        entity_manager.score += enemy.score_value
                        entity_manager.add_particles(enemy.x, enemy.y)
                    break

    def check_enemy_bullet_player_collisions(self, player, entity_manager):
        for bullet in entity_manager.enemy_bullets[:]:
            if player.collides_with(bullet):
                if player.shield_active:
                    entity_manager.enemy_bullets.remove(bullet)
                else:
                    player.take_damage()
                    entity_manager.enemy_bullets.remove(bullet)

    def check_enemy_player_collisions(self, player, enemies):
        for enemy in enemies:
            if player.collides_with(enemy):
                if not player.shield_active:
                    player.take_damage()

    def check_powerup_player_collisions(self, player, powerups, powerup_system):
        for powerup in powerups[:]:
            if player.collides_with(powerup):
                powerup_system.activate_powerup(player, powerup.type)
                powerups.remove(powerup)

    def check_sword_collision(self, player, enemies, graze_system):
        if not player.sword_active:
            return 0

        hits = 0
        sword_rect = pygame.Rect(
            player.x - player.size * 2,
            player.y - player.size * 2,
            player.size * 4,
            player.size * 4
        )
        for enemy in enemies[:]:
            if sword_rect.collidepoint(enemy.x, enemy.y):
                enemy.take_damage(player.sword_damage)
                graze_system.add_meter(5)
                hits += 1
                if enemy.health <= 0:
                    enemies.remove(enemy)
        return hits