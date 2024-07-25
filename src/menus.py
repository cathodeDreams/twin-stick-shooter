import pygame

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Menu settings
MENU_FONT_SIZE = 36
MENU_ITEM_HEIGHT = 50

def draw_menu(screen, menu_items, selected_index):
    menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    title_font = pygame.font.Font(None, MENU_FONT_SIZE * 2)

    screen.fill(BLACK)
    title = title_font.render("Twin Stick Shooter", True, WHITE)
    screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, screen.get_height() // 4))

    for i, item in enumerate(menu_items):
        color = GREEN if i == selected_index else WHITE
        text = menu_font.render(item, True, color)
        x = screen.get_width() // 2 - text.get_width() // 2
        y = screen.get_height() // 2 + i * MENU_ITEM_HEIGHT
        screen.blit(text, (x, y))

def main_menu(screen, joystick):
    menu_items = ["Start Game", "How to Play", "Exit"]
    selected_index = 0

    while True:
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
                        return "exit"
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:  # Left stick vertical
                    if event.value < -0.5 and selected_index > 0:
                        selected_index -= 1
                    elif event.value > 0.5 and selected_index < len(menu_items) - 1:
                        selected_index += 1

        draw_menu(screen, menu_items, selected_index)
        pygame.display.flip()

def guide_menu(screen, joystick):
    guide_font = pygame.font.Font(None, 24)
    title_font = pygame.font.Font(None, 36)

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
        "P: Piercing shot",
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

        screen.fill(BLACK)
        title = title_font.render("Game Guide", True, WHITE)
        screen.blit(title, (screen.get_width() // 2 - title.get_width() // 2, 20))

        for i, line in enumerate(guide_text):
            text = guide_font.render(line, True, WHITE)
            screen.blit(text, (50, 80 + i * 30))

        pygame.display.flip()

def pause_menu(screen, joystick):
    menu_items = ["Resume", "Exit to Main Menu"]
    selected_index = 0

    while True:
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
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:  # Left stick vertical
                    if event.value < -0.5 and selected_index > 0:
                        selected_index -= 1
                    elif event.value > 0.5 and selected_index < len(menu_items) - 1:
                        selected_index += 1

        draw_menu(screen, menu_items, selected_index)
        pygame.display.flip()

def game_over_menu(screen, joystick, score):
    menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
    menu_items = ["Continue", "Exit to Main Menu"]
    selected_index = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:  # A button
                    if selected_index == 0:
                        return "continue"
                    elif selected_index == 1:
                        return "main_menu"
            elif event.type == pygame.JOYAXISMOTION:
                if event.axis == 1:  # Left stick vertical
                    if event.value < -0.5 and selected_index > 0:
                        selected_index -= 1
                    elif event.value > 0.5 and selected_index < len(menu_items) - 1:
                        selected_index += 1

        screen.fill(BLACK)
        game_over_text = menu_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (screen.get_width() // 2 - game_over_text.get_width() // 2, 
                                     screen.get_height() // 3 - game_over_text.get_height() // 2))
        
        score_text = menu_font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (screen.get_width() // 2 - score_text.get_width() // 2, 
                                 screen.get_height() // 2 - score_text.get_height() // 2))

        draw_menu(screen, menu_items, selected_index)
        pygame.display.flip()