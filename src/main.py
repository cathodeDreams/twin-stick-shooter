import pygame
import sys
from game import Game
from menus import main_menu, pause_menu, game_over_menu, guide_menu

# Initialize Pygame
pygame.init()
pygame.joystick.init()

# Set up display
infoObject = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
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

def main():
    game = Game(screen, joystick)
    
    while True:
        menu_result = main_menu(screen, joystick)
        if menu_result == "exit":
            break
        elif menu_result == "start":
            game.reset()
            game_result = game_loop(game)
            if game_result == "exit":
                break
        elif menu_result == "guide":
            guide_menu(screen, joystick)

    pygame.quit()
    sys.exit()

def game_loop(game):
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 7:  # Start button
                    pause_result = pause_menu(screen, joystick)
                    if pause_result == "main_menu" or pause_result == "exit":
                        return pause_result

        game.handle_input()
        game.update_game_state()
        game.draw_game()

        if not game.player.alive:
            pygame.display.flip()
            pygame.time.wait(1000)  # Wait for a second before showing game over menu
            game_over_result = game_over_menu(screen, joystick, game.score)
            if game_over_result == "continue":
                game.reset()
            else:
                return game_over_result

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

if __name__ == "__main__":
    main()