import pygame
import sys
import requests
from utils import draw_button
from game import placement_phase

SERVER_URL = "http://127.0.0.1:8000"


def main_menu(screen, game_rooms_menu, settings_menu):
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
                        player2_name = input_player_name(screen, "Введите имя игрока 2:")
                        join_game(screen, game_id, player2_name)

        pygame.display.flip()
    main_menu(screen, game_rooms_menu, None)


def create_game(screen):
    player1_name = input_player_name(screen, "Введите имя игрока 1:")
    response = requests.post(f"{SERVER_URL}/create_game/", json={"player1_name": player1_name})
    data = response.json()
    if response.status_code == 200:
        game_id = data["game_id"]
        player = data["player"]
        placement_phase(screen, game_id, player)
    else:
        print(data["detail"])


def join_game(screen, game_id, player2_name):
    response = requests.post(f"{SERVER_URL}/join_game/", json={"game_id": game_id, "player2_name": player2_name})
    data = response.json()
    if response.status_code == 200:
        player = data["player"]
        placement_phase(screen, game_id, player)
    else:
        print(data["detail"])


def input_player_name(screen, prompt):
    """Функция для ввода имени игрока."""
    font = pygame.font.SysFont('Arial', 24)
    input_box = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2, 200, 50)
    color_inactive = pygame.Color('lightskyblue3')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        done = True
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((255, 255, 255))
        txt_surface = font.render(prompt, True, (0, 0, 0))
        screen.blit(txt_surface,
                    (screen.get_width() // 2 - txt_surface.get_width() // 2, screen.get_height() // 2 - 50))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
    return text


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
