import pygame

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)


def draw_button(screen, text, rect, color):
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.SysFont('Arial', 30)
    text = str(text)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
    screen.blit(label, label_rect)
