import pygame
import sys
from utils import draw_button


def main_menu(screen, game_loop, settings_menu):
    run = True
    while run:
        screen.fill((255, 255, 255))

        play_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 150, 200, 50)
        settings_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 50, 200, 50)
        quit_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 50, 200, 50)

        draw_button(screen, "Играть", play_button, (169, 169, 169))
        draw_button(screen, "Настройки", settings_button, (169, 169, 169))
        draw_button(screen, "Выйти", quit_button, (169, 169, 169))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    game_loop(screen)
                if settings_button.collidepoint(event.pos):
                    settings_menu(screen)
                if quit_button.collidepoint(event.pos):
                    run = False

        pygame.display.flip()
    pygame.quit()
    sys.exit()


def settings_menu(screen):
    run = True
    while run:
        screen.fill((255, 255, 255))
        font = pygame.font.SysFont('Arial', 50)
        label = font.render('Настройки', True, (0, 0, 0))
        label_rect = label.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 200))
        screen.blit(label, label_rect)

        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 200, 200, 50)
        draw_button(screen, "Назад", back_button, (169, 169, 169))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    run = False

        pygame.display.flip()
