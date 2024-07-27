import pygame
import sys
from game_manager import GameManager, GameState
from player import Player
from entity_manager import EntityManager
from collision_manager import CollisionManager
from renderer import Renderer
from grazing_system import GrazingSystem
from powerup_system import PowerUpSystem
from enemy_behavior import EnemyBehavior
from menus import main_menu, pause_menu, game_over_menu, guide_menu
from settings import Settings
from settings_menu import SettingsMenu

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Load settings
settings = Settings()
settings.load_settings('settings.ini')

# Set up display
if settings.display_mode == "fullscreen":
    screen = pygame.display.set_mode(settings.resolution, pygame.FULLSCREEN)
elif settings.display_mode == "borderless":
    screen = pygame.display.set_mode(settings.resolution, pygame.NOFRAME)
else:
    screen = pygame.display.set_mode(settings.resolution)

pygame.display.set_caption("Twin Stick Shooter")

# Initialize joystick
joystick = None
try:
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    else:
        print("No joystick detected. Please connect a joystick and restart the game.")
        pygame.quit()
        sys.exit()
except pygame.error as e:
    print(f"Joystick error: {e}")
    print("The game requires a joystick to play. Please connect one and restart the game.")
    pygame.quit()
    sys.exit()

def create_game_manager():
    arena_rect = pygame.Rect(50, 50, settings.resolution[0] - 100, settings.resolution[1] - 100)
    player = Player(settings.resolution[0] // 2, settings.resolution[1] // 2, arena_rect)
    entity_manager = EntityManager(arena_rect)
    collision_manager = CollisionManager()
    renderer = Renderer(screen, arena_rect)
    graze_system = GrazingSystem()
    powerup_system = PowerUpSystem(settings.resolution[0], settings.resolution[1])
    enemy_behavior = EnemyBehavior()

    return GameManager(screen, joystick, player, entity_manager, collision_manager,
                       renderer, graze_system, powerup_system, enemy_behavior, arena_rect)

def main():
    try:
        game_manager = create_game_manager()
        settings_menu = SettingsMenu(screen, settings)
        
        current_screen = "main_menu"
        
        while True:
            try:
                if current_screen == "main_menu":
                    menu_result = main_menu(screen, joystick)
                    if menu_result == "exit":
                        break
                    elif menu_result == "start":
                        game_manager.reset()
                        current_screen = "game"
                    elif menu_result == "guide":
                        current_screen = "guide"
                    elif menu_result == "settings":
                        current_screen = "settings"
                elif current_screen == "game":
                    game_result = game_loop(game_manager)
                    if game_result == "exit":
                        break
                    elif game_result == "main_menu":
                        current_screen = "main_menu"
                    elif game_result == "settings":
                        current_screen = "settings"
                elif current_screen == "guide":
                    guide_result = guide_menu(screen, joystick)
                    if guide_result == "main_menu":
                        current_screen = "main_menu"
                elif current_screen == "settings":
                    settings_result = settings_loop(settings_menu)
                    if settings_result == "main_menu":
                        current_screen = "main_menu"
                    elif settings_result == "game":
                        current_screen = "game"
                    elif settings_result == "exit":
                        break
            except Exception as e:
                print(f"Error in main loop: {str(e)}")
                current_screen = "main_menu"
    except Exception as e:
        print(f"Critical error: {str(e)}")
    finally:
        pygame.quit()
        sys.exit()

def game_loop(game_manager):
    clock = pygame.time.Clock()

    try:
        while not game_manager.is_game_over:
            try:
                clock.tick(settings.framerate)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "exit"
                    elif event.type == pygame.JOYBUTTONDOWN:
                        if event.button == 7:  # Start button
                            game_manager.toggle_pause()

                if game_manager.is_paused:
                    pause_result = pause_menu(screen, joystick)
                    if pause_result in ["main_menu", "settings", "exit"]:
                        return pause_result
                    game_manager.toggle_pause()
                else:
                    game_manager.handle_input()
                    game_manager.update_game_state()
                    game_manager.draw_game()

                pygame.display.flip()
            except Exception as e:
                print(f"Error in game loop iteration: {str(e)}")
                return "main_menu"

    except Exception as e:
        print(f"Error in game loop: {str(e)}")
        return "main_menu"

    # Game over
    pygame.time.wait(1000)
    game_over_result = game_over_menu(screen, joystick, game_manager.score)
    if game_over_result == "continue":
        game_manager.reset()
        return game_loop(game_manager)
    else:
        return game_over_result

def settings_loop(settings_menu):
    clock = pygame.time.Clock()
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            result = settings_menu.handle_input(event)
            if result == "main_menu":
                return "main_menu"
            elif result == "game":
                return "game"

        settings_menu.draw()
        pygame.display.flip()

if __name__ == "__main__":
    main()