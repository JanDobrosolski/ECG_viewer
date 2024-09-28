import pygame

from utils.constants import WHITE, BLACK

def draw_button(screen, rect, color, text, font, text_color):
    pygame.draw.rect(screen, color, rect)
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    screen.blit(text_surface, text_rect)

def draw_radio_button(screen, rect, color, text, font, text_color, selected):
    pygame.draw.rect(screen, color if selected else WHITE, rect)
    pygame.draw.rect(screen, BLACK, rect, 2)
    text_surface = font.render(text, True, text_color)
    screen.blit(text_surface, (rect.x + 30, rect.y - 5))
