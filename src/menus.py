import pygame
from colors import Colors

# Menu settings
MENU_FONT_SIZE = 36
MENU_ITEM_HEIGHT = 50
MENU_FPS = 30
MENU_INPUT_DELAY = 200

def draw_menu(screen, menu_items, selected_index):
    menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    title_font = pygame.font.Font(None, MENU_FONT_SIZE * 2)

    screen.fill(Colors.BACKGROUND)
    title = title_font.render("Twin Stick Shooter", True, Colors.FOREGROUND)
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, screen.get_height() // 4))

    for i, item in enumerate(menu_items):
        color = Colors.GREEN if i == selected_index else Colors.COMMENT
        text = menu_font.render(item, True, color)
        x = screen.get_width() // 2 - text.get_width() // 2
        y = screen.get_height() // 2 + i * MENU_ITEM_HEIGHT
        screen.blit(text, (x, y))

def main_menu(screen, joystick):
    menu_items = ["Start Game", "How to Play", "Settings", "Exit"]
    selected_index = 0
    clock = pygame.time.Clock()
    last_input_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    if selected_index == 0:
                        return "start"
                    elif selected_index == 1:
                        guide_menu(screen, joystick)
                    elif selected_index == 2:
                        return "settings"
                    elif selected_index == 3:
                        return "exit"

        if current_time - last_input_time > MENU_INPUT_DELAY:
            axis_value = joystick.get_axis(1)  # Left stick vertical
            if axis_value < -0.5 and selected_index > 0:
                selected_index -= 1
                last_input_time = current_time
            elif axis_value > 0.5 and selected_index < len(menu_items) - 1:
                selected_index += 1
                last_input_time = current_time

        draw_menu(screen, menu_items, selected_index)
        pygame.display.flip()
        clock.tick(MENU_FPS)

def guide_menu(screen, joystick):
    guide_font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 36)
    clock = pygame.time.Clock()

    guide_text = [
        "How to Play:",
        "",
        "- Use left stick to move",
        "- Use right stick to aim and shoot",
        "- Press right bumper for sword attack",
        "- Press left bumper to activate shield",
        "",
        "Powerups:",
        "S: Spread shot",
        "L: Laser",
        "H: Homing missiles",
        "M: Multi-shot",
        "D: Shield",
        "B: Bomb",
        "",
        "Press A to return to main menu"
    ]

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    return

        screen.fill(Colors.BACKGROUND)
        title = title_font.render("Game Guide", True, Colors.FOREGROUND)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))

        for i, line in enumerate(guide_text):
            text = guide_font.render(line, True, Colors.FOREGROUND)
            screen.blit(text, (50, 80 + i * 30))

        pygame.display.flip()
        clock.tick(MENU_FPS)

def pause_menu(screen, joystick):
    menu_items = ["Resume", "Settings", "Exit to Main Menu"]
    selected_index = 0
    clock = pygame.time.Clock()
    last_input_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    if selected_index == 0:
                        return "resume"
                    elif selected_index == 1:
                        return "main_menu"
                elif event.button == 7:  # Start button
                    return "resume"

        if current_time - last_input_time > MENU_INPUT_DELAY:
            axis_value = joystick.get_axis(1)  # Left stick vertical
            if axis_value < -0.5 and selected_index > 0:
                selected_index -= 1
                last_input_time = current_time
            elif axis_value > 0.5 and selected_index < len(menu_items) - 1:
                selected_index += 1
                last_input_time = current_time

        draw_menu(screen, menu_items, selected_index)
        pygame.display.flip()
        clock.tick(MENU_FPS)

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

def game_over_menu(screen, joystick, score):
    menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    menu_items = ["Continue", "Exit to Main Menu"]
    selected_index = 0
    clock = pygame.time.Clock()
    last_input_time = pygame.time.get_ticks()

    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    if selected_index == 0:
                        return "continue"
                    elif selected_index == 1:
                        return "main_menu"

        if current_time - last_input_time > MENU_INPUT_DELAY:
            axis_value = joystick.get_axis(1)  # Left stick vertical
            if axis_value < -0.5 and selected_index > 0:
                selected_index -= 1
                last_input_time = current_time
            elif axis_value > 0.5 and selected_index < len(menu_items) - 1:
                selected_index += 1
                last_input_time = current_time

        screen.fill(Colors.BACKGROUND)
        game_over_text = menu_font.render("GAME OVER", True, Colors.RED)
        screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 
                                     screen.get_height() // 3 - game_over_text.get_height() // 2))
        
        score_text = menu_font.render(f"Final Score: {score}", True, Colors.FOREGROUND)
        screen.blit(score_text, (screen.get_width() // 2 - score_text.get_width() // 2, 
                                 screen.get_height() // 2 - score_text.get_height() // 2))

        draw_menu(screen, menu_items, selected_index)
        pygame.display.flip()
        clock.tick(MENU_FPS)