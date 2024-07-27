import pygame

def apply_glow_and_shadow(surface, color, pos, size, glow_intensity=0.5, shadow_offset=(5, 5)):
    glow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
    shadow_surface = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
    
    # Draw multiple circles with decreasing opacity to simulate glow
    for i in range(10, 0, -1):
        glow_size = size * (1 + i * 0.1)
        glow_opacity = int(glow_intensity * 255 * (1 - i * 0.1))
        pygame.draw.circle(glow_surface, (*color, glow_opacity), (size * 2, size * 2), glow_size)
    
    # Draw shadow
    shadow_color = (0, 0, 0, 100)
    pygame.draw.circle(shadow_surface, shadow_color, (size * 2 + shadow_offset[0], size * 2 + shadow_offset[1]), size)
    
    # Apply surfaces to the main surface
    surface.blit(shadow_surface, (pos[0] - size * 2 + shadow_offset[0], pos[1] - size * 2 + shadow_offset[1]))
    surface.blit(glow_surface, (pos[0] - size * 2, pos[1] - size * 2))