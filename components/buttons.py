import pygame

from utils.constants import BLACK, DARK_GRAY, GRADIENT_COLOR_1, GRADIENT_COLOR_2

def draw_button(screen, rect, color, text, font, text_color, hover=False):
    # Gradient fill for the button
    gradient_surface = pygame.Surface((rect.width, rect.height))
    for y in range(rect.height):
        blend_ratio = y / rect.height
        blended_color = [
            int(GRADIENT_COLOR_1[i] * (1 - blend_ratio) + GRADIENT_COLOR_2[i] * blend_ratio)
            for i in range(3)
        ]
        pygame.draw.line(gradient_surface, blended_color, (0, y), (rect.width, y))
    
    screen.blit(gradient_surface, (rect.x, rect.y))
    
    # Rounded rectangle border
    border_radius = 10
    pygame.draw.rect(screen, DARK_GRAY if hover else color, rect, border_radius=border_radius)

    # Text
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_radio_button(screen, rect, color, text, font, text_color, selected):
    # Draw circular radio button
    center = (rect.x + 10, rect.y + rect.height // 2)
    radius = 10
    pygame.draw.circle(screen, BLACK, center, radius, 2)
    if selected:
        pygame.draw.circle(screen, color, center, radius - 4)

    # Draw label next to radio button
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (rect.x + 30, rect.y))

def handle_hover_effect(button_rect, mouse_pos):
    return button_rect.collidepoint(mouse_pos)
