import pygame
from colors import Colors

class SettingsMenu:
    def __init__(self, screen, settings):
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.Font(None, 32)
        self.resolutions = [settings.native_resolution, (1920, 1080), (1600, 900), (1366, 768), (1280, 720)]
        self.refresh_rates = [60, 75, 120, 144]
        self.selected_index = 0
        self.menu_items = [
            "Resolution",
            "Refresh Rate",
            "Display Mode",
            "Music Volume",
            "SFX Volume",
            "Difficulty",
            "Apply Changes",
            "Back"
        ]
        self.input_delay = 200
        self.last_input_time = 0

    def draw(self):
        self.screen.fill(Colors.BACKGROUND)
        for i, item in enumerate(self.menu_items):
            color = Colors.GREEN if i == self.selected_index else Colors.FOREGROUND
            text = self.font.render(item, True, color)
            self.screen.blit(text, (100, 100 + i * 50))

        # Display current settings
        res_text = f"Current: {self.settings.resolution[0]}x{self.settings.resolution[1]}"
        refresh_text = f"Current: {self.settings.framerate} Hz"
        mode_text = f"Current: {self.settings.display_mode}"
        music_text = f"Current: {int(self.settings.music_volume * 100)}%"
        sfx_text = f"Current: {int(self.settings.sfx_volume * 100)}%"
        diff_text = f"Current: {self.settings.difficulty}"
        
        self.screen.blit(self.font.render(res_text, True, Colors.COMMENT), (400, 100))
        self.screen.blit(self.font.render(refresh_text, True, Colors.COMMENT), (400, 150))
        self.screen.blit(self.font.render(mode_text, True, Colors.COMMENT), (400, 200))
        self.screen.blit(self.font.render(music_text, True, Colors.COMMENT), (400, 250))
        self.screen.blit(self.font.render(sfx_text, True, Colors.COMMENT), (400, 300))
        self.screen.blit(self.font.render(diff_text, True, Colors.COMMENT), (400, 350))

    def handle_input(self, event):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_input_time < self.input_delay:
            return None

        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # A button
                self.last_input_time = current_time
                return self.select_option()
            elif event.button == 1:  # B button
                self.last_input_time = current_time
                return "main_menu"
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 1:  # Vertical axis
                if event.value < -0.5:  # Up
                    self.selected_index = (self.selected_index - 1) % len(self.menu_items)
                    self.last_input_time = current_time
                elif event.value > 0.5:  # Down
                    self.selected_index = (self.selected_index + 1) % len(self.menu_items)
                    self.last_input_time = current_time
            elif event.axis == 0:  # Horizontal axis
                if event.value > 0.5:  # Right
                    self.increment_setting()
                    self.last_input_time = current_time
                elif event.value < -0.5:  # Left
                    self.decrement_setting()
                    self.last_input_time = current_time
        return None

    def select_option(self):
        if self.selected_index == 6:  # Apply Changes
            self.apply_changes()
        elif self.selected_index == 7:  # Back
            return "main_menu"
        return None

    def increment_setting(self):
        if self.selected_index == 0:  # Resolution
            current_index = self.resolutions.index(self.settings.resolution)
            self.settings.resolution = self.resolutions[(current_index + 1) % len(self.resolutions)]
        elif self.selected_index == 1:  # Refresh Rate
            current_index = self.refresh_rates.index(self.settings.framerate)
            self.settings.framerate = self.refresh_rates[(current_index + 1) % len(self.refresh_rates)]
        elif self.selected_index == 2:  # Display Mode
            modes = ["windowed", "fullscreen", "borderless"]
            current_index = modes.index(self.settings.display_mode)
            self.settings.display_mode = modes[(current_index + 1) % len(modes)]
        elif self.selected_index == 3:  # Music Volume
            self.settings.music_volume = min(1.0, self.settings.music_volume + 0.1)
        elif self.selected_index == 4:  # SFX Volume
            self.settings.sfx_volume = min(1.0, self.settings.sfx_volume + 0.1)
        elif self.selected_index == 5:  # Difficulty
            difficulties = ["easy", "normal", "hard"]
            current_index = difficulties.index(self.settings.difficulty)
            self.settings.difficulty = difficulties[(current_index + 1) % len(difficulties)]

    def decrement_setting(self):
        if self.selected_index == 0:  # Resolution
            current_index = self.resolutions.index(self.settings.resolution)
            self.settings.resolution = self.resolutions[(current_index - 1) % len(self.resolutions)]
        elif self.selected_index == 1:  # Refresh Rate
            current_index = self.refresh_rates.index(self.settings.framerate)
            self.settings.framerate = self.refresh_rates[(current_index - 1) % len(self.refresh_rates)]
        elif self.selected_index == 2:  # Display Mode
            modes = ["windowed", "fullscreen", "borderless"]
            current_index = modes.index(self.settings.display_mode)
            self.settings.display_mode = modes[(current_index - 1) % len(modes)]
        elif self.selected_index == 3:  # Music Volume
            self.settings.music_volume = max(0.0, self.settings.music_volume - 0.1)
        elif self.selected_index == 4:  # SFX Volume
            self.settings.sfx_volume = max(0.0, self.settings.sfx_volume - 0.1)
        elif self.selected_index == 5:  # Difficulty
            difficulties = ["easy", "normal", "hard"]
            current_index = difficulties.index(self.settings.difficulty)
            self.settings.difficulty = difficulties[(current_index - 1) % len(difficulties)]

    def apply_changes(self):
        self.settings.apply_display_settings()
        self.settings.save_settings('settings.ini')
        print("Settings applied and saved.")  # For debugging