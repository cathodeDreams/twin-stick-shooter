import random
from powerup import PowerUp

class PowerUpSystem:
    def __init__(self, screen_width, screen_height):
        self.powerups = []
        self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb"]
        self.powerup_duration = 600  # 10 seconds at 60 FPS
        self.wave_number = 1
        self.max_powerups = 3
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.spawn_timer = 0
        self.spawn_interval = 300  # Spawn attempt every 5 seconds (assuming 60 FPS)

    def reset(self):
        self.powerups = []
        self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb"]
        self.wave_number = 1
        self.spawn_timer = 0

    def update(self, player, graze_level, wave):
        self.wave_number = wave
        self.spawn_timer += 1
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_powerups()
            self.spawn_timer = 0
        self.update_player_powerup(player)

    def spawn_powerups(self):
        if self.wave_number >= 2 and len(self.powerups) < self.max_powerups:
            if random.random() < 0.3:  # 30% chance to spawn a powerup
                x = random.randint(50, self.screen_width - 50)
                y = random.randint(50, self.screen_height - 50)
            
                if not self.available_powerups:
                    self.available_powerups = ["spread", "laser", "homing", "multishot", "shield", "bomb"]
            
                powerup_type = random.choice(self.available_powerups)
                new_powerup = PowerUp(x, y, powerup_type)
                self.powerups.append(new_powerup)
                self.available_powerups.remove(powerup_type)
                print(f"Spawned {powerup_type} powerup at ({x}, {y})")  # Debug print

    def activate_powerup(self, player, powerup_type):
        player.current_weapon = powerup_type
        player.powerup_timer = self.powerup_duration
        if powerup_type == "shield":
            player.activate_shield()
        print(f"Activated {powerup_type} powerup")  # Debug print

    def update_player_powerup(self, player):
        if player.powerup_timer > 0:
            player.powerup_timer -= 1
            if player.powerup_timer <= 0:
                player.current_weapon = "default"
                print("Powerup expired")  # Debug print