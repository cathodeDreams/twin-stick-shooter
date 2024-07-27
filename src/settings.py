import pygame
import configparser
import os

class Settings:
    def __init__(self):
        pygame.init()  # Ensure pygame is initialized
        info = pygame.display.Info()
        self.native_resolution = (info.current_w, info.current_h)
        self.display_mode = "windowed"
        self.resolution = self.native_resolution
        self.framerate = 60
        self.music_volume = 0.7
        self.sfx_volume = 0.5
        self.difficulty = "normal"
        self.control_scheme = "default"

    def load_settings(self, filename):
        config = configparser.ConfigParser()
        
        if os.path.exists(filename):
            config.read(filename)
            
            if 'Display' in config:
                self.display_mode = config.get('Display', 'mode', fallback=self.display_mode)
                res = config.get('Display', 'resolution', fallback=f"{self.resolution[0]},{self.resolution[1]}")
                self.resolution = tuple(map(int, res.split(',')))
                self.framerate = config.getint('Display', 'framerate', fallback=self.framerate)
            
            if 'Audio' in config:
                self.music_volume = config.getfloat('Audio', 'music_volume', fallback=self.music_volume)
                self.sfx_volume = config.getfloat('Audio', 'sfx_volume', fallback=self.sfx_volume)
            
            if 'Gameplay' in config:
                self.difficulty = config.get('Gameplay', 'difficulty', fallback=self.difficulty)
                self.control_scheme = config.get('Gameplay', 'control_scheme', fallback=self.control_scheme)
        else:
            print(f"Settings file {filename} not found. Using default settings.")

    def save_settings(self, filename):
        config = configparser.ConfigParser()

        config['Display'] = {
            'mode': self.display_mode,
            'resolution': f"{self.resolution[0]},{self.resolution[1]}",
            'framerate': str(self.framerate)
        }

        config['Audio'] = {
            'music_volume': str(self.music_volume),
            'sfx_volume': str(self.sfx_volume)
        }

        config['Gameplay'] = {
            'difficulty': self.difficulty,
            'control_scheme': self.control_scheme
        }

        with open(filename, 'w') as configfile:
            config.write(configfile)

    def apply_display_settings(self):
        import pygame  # Import here to avoid circular import
        if self.display_mode == "fullscreen":
            pygame.display.set_mode(self.resolution, pygame.FULLSCREEN)
        elif self.display_mode == "borderless":
            pygame.display.set_mode(self.resolution, pygame.NOFRAME)
        else:
            pygame.display.set_mode(self.resolution)

    def toggle_fullscreen(self):
        if self.display_mode == "fullscreen":
            self.display_mode = "windowed"
        else:
            self.display_mode = "fullscreen"
        self.apply_display_settings()

    def set_resolution(self, width, height):
        self.resolution = (width, height)
        self.apply_display_settings()

    def set_framerate(self, framerate):
        self.framerate = framerate

    def set_music_volume(self, volume):
        self.music_volume = max(0.0, min(1.0, volume))

    def set_sfx_volume(self, volume):
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_difficulty(self, difficulty):
        if difficulty in ["easy", "normal", "hard"]:
            self.difficulty = difficulty
        else:
            print(f"Invalid difficulty setting: {difficulty}")

    def set_control_scheme(self, scheme):
        self.control_scheme = scheme