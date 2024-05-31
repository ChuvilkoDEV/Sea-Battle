import pygame
import sys
import requests
import uuid
from utils import draw_button
from game import placement_phase

SERVER_URL = "http://127.0.0.1:8000"


def main_menu(screen, game_rooms_menu, settings_menu):
    """
    Функция отображает главное меню игры.
    В меню можно выбрать "Играть", "Настройки" или "Выйти".
    """
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
                    game_rooms_menu(screen)
                if settings_button.collidepoint(event.pos):
                    settings_menu(screen)
                if quit_button.collidepoint(event.pos):
                    run = False

        pygame.display.flip()
    pygame.quit()
    sys.exit()


def game_rooms_menu(screen):
    """
    Функция отображает меню комнат игры.
    Пользователь может выбрать существующую комнату или создать новую.
    """
    run = True
    while run:
        screen.fill((255, 255, 255))
        response = requests.get(f"{SERVER_URL}/get_games/")
        games = response.json().get("games", [])

        font = pygame.font.SysFont('Arial', 24)
        y_offset = 100
        if games:
            for game_id in games:
                game_button = pygame.Rect(screen.get_width() // 2 - 100, y_offset, 200, 50)
                draw_button(screen, game_id, game_button, (169, 169, 169))
                y_offset += 70
        else:
            no_games_label = font.render('Нет доступных комнат', True, (0, 0, 0))
            no_games_rect = no_games_label.get_rect(center=(screen.get_width() // 2, y_offset))
            screen.blit(no_games_label, no_games_rect)

        create_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 100, 200, 50)
        draw_button(screen, "Создать комнату", create_button, (169, 169, 169))
        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 200, 200, 50)
        draw_button(screen, "Назад", back_button, (169, 169, 169))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if create_button.collidepoint(event.pos):
                    create_game(screen)
                if back_button.collidepoint(event.pos):
                    run = False
                for i, game_id in enumerate(games):
                    if pygame.Rect(screen.get_width() // 2 - 100, 100 + i * 70, 200, 50).collidepoint(event.pos):
                        placement_phase(screen, game_id)

        pygame.display.flip()


def create_game(screen):
    """
    Функция позволяет создать новую игру, вводя имя игрока. ID игры генерируется автоматически.
    """
    run = True
    player_name = ""
    name_box = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 25, 200, 50)

    while run:
        screen.fill((255, 255, 255))
        font = pygame.font.SysFont('Arial', 24)
        label_font = pygame.font.SysFont('Arial', 20)

        # Добавление подписи к полю ввода имени игрока
        player_name_label = label_font.render("Имя Игрока:", True, (0, 0, 0))
        screen.blit(player_name_label, (name_box.x, name_box.y - 25))

        create_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 50, 200, 50)
        draw_button(screen, "Создать", create_button, (169, 169, 169))
        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 100, 200, 50)
        draw_button(screen, "Назад", back_button, (169, 169, 169))

        pygame.draw.rect(screen, (0, 0, 0), name_box, 2)

        player_name_surface = font.render(player_name, True, (0, 0, 0))
        screen.blit(player_name_surface, (name_box.x + 5, name_box.y + 5))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if create_button.collidepoint(event.pos):
                    game_id = str(uuid.uuid4())  # Генерация уникального ID для игры
                    # Ensure the payload matches the expected format
                    response = requests.post(f"{SERVER_URL}/create_game/",
                                             json={"player1_name": player_name})
                    if response.status_code == 200:
                        placement_phase(screen, game_id)
                if back_button.collidepoint(event.pos):
                    run = False
            if event.type == pygame.KEYDOWN:
                if name_box.collidepoint(pygame.mouse.get_pos()):
                    if event.key == pygame.K_BACKSPACE:
                        player_name = player_name[:-1]
                    else:
                        player_name += event.unicode

        pygame.display.flip()



def settings_menu(screen):
    """
    Функция отображает меню настроек игры.
    """
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
