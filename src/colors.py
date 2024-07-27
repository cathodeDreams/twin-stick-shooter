class Colors:
    # Dracula color palette
    BACKGROUND = (40, 42, 54)
    CURRENT_LINE = (68, 71, 90)
    FOREGROUND = (248, 248, 242)
    COMMENT = (98, 114, 164)
    CYAN = (139, 233, 253)
    GREEN = (80, 250, 123)
    ORANGE = (255, 184, 108)
    PINK = (255, 121, 198)
    PURPLE = (189, 147, 249)
    RED = (255, 85, 85)
    YELLOW = (241, 250, 140)

    # Game-specific colors
    BACKGROUND_COLOR = BACKGROUND
    UI_BACKGROUND_COLOR = CURRENT_LINE
    BORDER_COLOR = COMMENT
    PLAYER_COLOR = FOREGROUND
    BULLET_COLOR = CYAN
    ENEMY_COLOR = RED
    BOSS_COLOR = PINK
    SHIELD_COLOR = PURPLE
    GRAZE_INNER_COLOR = RED
    GRAZE_OUTER_COLOR = PURPLE

    POWERUP_COLORS = {
        "spread": ORANGE,
        "laser": CYAN,
        "homing": PINK,
        "multishot": YELLOW,
        "shield": PURPLE,
        "bomb": RED,
        "piercing": GREEN
    }