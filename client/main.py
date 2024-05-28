# main.py
import pygame
import sys
from menu import main_menu, game_rooms_menu, settings_menu
from game import game_loop

# Инициализация Pygame
pygame.init()

# Определение размеров окна
WIDTH, HEIGHT = 900, 600

# Создание окна
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Морской бой")

if __name__ == "__main__":
    main_menu(WIN, game_rooms_menu, settings_menu)
