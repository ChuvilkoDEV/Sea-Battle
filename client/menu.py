# menu.py
import pygame  # Импортируем модуль Pygame для работы с графикой и игровым циклом
import sys  # Импортируем модуль sys для выхода из программы
import requests  # Импортируем модуль requests для выполнения HTTP-запросов
from utils import draw_button  # Импортируем функцию draw_button из модуля utils для отрисовки кнопок
from game import game_loop  # Импортируем функцию game_loop из модуля game для запуска игрового цикла

SERVER_URL = "http://127.0.0.1:8000"  # Устанавливаем URL сервера для API-запросов


def main_menu(screen, game_rooms_menu, settings_menu):  # Функция главного меню
    run = True  # Устанавливаем флаг выполнения цикла
    while run:  # Запускаем цикл меню
        screen.fill((255, 255, 255))  # Заполняем экран белым цветом

        # Создаем кнопки "Играть", "Настройки" и "Выйти" с заданными размерами и положением
        play_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 150, 200, 50)
        settings_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 50, 200, 50)
        quit_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 50, 200, 50)

        # Отрисовываем кнопки с помощью функции draw_button
        draw_button(screen, "Играть", play_button, (169, 169, 169))
        draw_button(screen, "Настройки", settings_button, (169, 169, 169))
        draw_button(screen, "Выйти", quit_button, (169, 169, 169))

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если событие выхода
                run = False  # Прекращаем выполнение цикла
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                if play_button.collidepoint(event.pos):  # Если нажата кнопка "Играть"
                    game_rooms_menu(screen)  # Переходим в меню комнат игры
                if settings_button.collidepoint(event.pos):  # Если нажата кнопка "Настройки"
                    settings_menu(screen)  # Переходим в меню настроек
                if quit_button.collidepoint(event.pos):  # Если нажата кнопка "Выйти"
                    run = False  # Прекращаем выполнение цикла

        pygame.display.flip()  # Обновляем экран
    pygame.quit()  # Выходим из Pygame
    sys.exit()  # Выходим из программы


def game_rooms_menu(screen):  # Функция меню комнат игры
    run = True  # Устанавливаем флаг выполнения цикла
    while run:  # Запускаем цикл меню
        screen.fill((255, 255, 255))  # Заполняем экран белым цветом

        # Выполняем GET-запрос для получения списка игр
        response = requests.get(f"{SERVER_URL}/get_games/")
        games = response.json().get("games", [])  # Получаем список игр из ответа

        font = pygame.font.SysFont('Arial', 24)  # Устанавливаем шрифт
        y_offset = 100  # Начальное смещение по оси Y для кнопок игр
        for game_id in games:  # Для каждой игры в списке
            game_button = pygame.Rect(screen.get_width() // 2 - 100, y_offset, 200, 50)  # Создаем кнопку игры
            draw_button(screen, game_id, game_button, (169, 169, 169))  # Отрисовываем кнопку
            y_offset += 70  # Увеличиваем смещение по оси Y

        # Создаем кнопки "Создать комнату" и "Назад" с заданными размерами и положением
        create_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 100, 200, 50)
        draw_button(screen, "Создать комнату", create_button, (169, 169, 169))
        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 200, 200, 50)
        draw_button(screen, "Назад", back_button, (169, 169, 169))

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если событие выхода
                run = False  # Прекращаем выполнение цикла
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                if create_button.collidepoint(event.pos):  # Если нажата кнопка "Создать комнату"
                    create_game(screen)  # Переходим к созданию новой игры
                if back_button.collidepoint(event.pos):  # Если нажата кнопка "Назад"
                    run = False  # Прекращаем выполнение цикла
                for i, game_id in enumerate(games):  # Для каждой игры в списке
                    if pygame.Rect(screen.get_width() // 2 - 100, 100 + i * 70, 200, 50).collidepoint(event.pos):
                        game_loop(screen, game_id)  # Запускаем игровую сессию для выбранной игры

        pygame.display.flip()  # Обновляем экран


def create_game(screen):  # Функция создания новой игры
    run = True  # Устанавливаем флаг выполнения цикла
    game_id = ""  # Инициализируем переменную для ID игры
    player_name = ""  # Инициализируем переменную для имени игрока
    input_box = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 25, 200,
                            50)  # Создаем поле ввода ID игры
    name_box = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 - 100, 200,
                           50)  # Создаем поле ввода имени игрока

    while run:  # Запускаем цикл создания игры
        screen.fill((255, 255, 255))  # Заполняем экран белым цветом
        font = pygame.font.SysFont('Arial', 24)  # Устанавливаем шрифт
        create_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 50, 200, 50)
        draw_button(screen, "Создать", create_button, (169, 169, 169))  # Создаем и отрисовываем кнопку "Создать"
        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() - 100, 200, 50)
        draw_button(screen, "Назад", back_button, (169, 169, 169))  # Создаем и отрисовываем кнопку "Назад"

        pygame.draw.rect(screen, (0, 0, 0), input_box, 2)  # Отрисовываем поле ввода ID игры
        pygame.draw.rect(screen, (0, 0, 0), name_box, 2)  # Отрисовываем поле ввода имени игрока

        game_id_surface = font.render(game_id, True, (0, 0, 0))  # Рендерим текст ID игры
        player_name_surface = font.render(player_name, True, (0, 0, 0))  # Рендерим текст имени игрока
        screen.blit(game_id_surface, (input_box.x + 5, input_box.y + 5))  # Отображаем текст ID игры на экране
        screen.blit(player_name_surface, (name_box.x + 5, name_box.y + 5))  # Отображаем текст имени игрока на экране

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если событие выхода
                run = False  # Прекращаем выполнение цикла
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                if create_button.collidepoint(event.pos):  # Если нажата кнопка "Создать"
                    response = requests.post(f"{SERVER_URL}/create_game/",
                                             json={"game_id": game_id,
                                                   "player_name": player_name})  # Выполняем POST-запрос для создания игры
                    if response.status_code == 200:  # Если запрос выполнен успешно
                        game_loop(screen, game_id)  # Запускаем игровую сессию
                if back_button.collidepoint(event.pos):  # Если нажата кнопка "Назад"
                    run = False  # Прекращаем выполнение цикла
            if event.type == pygame.KEYDOWN:  # Если нажата клавиша
                if input_box.collidepoint(pygame.mouse.get_pos()):  # Если мышь находится над полем ввода ID игры
                    if event.key == pygame.K_BACKSPACE:  # Если нажата клавиша Backspace
                        game_id = game_id[:-1]  # Удаляем последний символ из ID игры
                    else:
                        game_id += event.unicode  # Добавляем символ к ID игры
                elif name_box.collidepoint(pygame.mouse.get_pos()):  # Если мышь находится над полем ввода имени игрока
                    if event.key == pygame.K_BACKSPACE:  # Если нажата клавиша Backspace
                        player_name = player_name[:-1]  # Удаляем последний символ из имени игрока
                    else:
                        player_name += event.unicode  # Добавляем символ к имени игрока

        pygame.display.flip()  # Обновляем экран


def settings_menu(screen):  # Функция меню настроек
    run = True  # Устанавливаем флаг выполнения цикла
    while run:  # Запускаем цикл меню
        screen.fill((255, 255, 255))  # Заполняем экран белым цветом
        font = pygame.font.SysFont('Arial', 50)  # Устанавливаем шрифт
        label = font.render('Настройки', True, (0, 0, 0))  # Рендерим текст "Настройки"
        label_rect = label.get_rect(
        center=(screen.get_width() // 2, screen.get_height() // 2 - 200))  # Центрируем текст на экране
        screen.blit(label, label_rect)  # Отображаем текст "Настройки" на экране

        back_button = pygame.Rect(screen.get_width() // 2 - 100, screen.get_height() // 2 + 200, 200, 50)
        draw_button(screen, "Назад", back_button, (169, 169, 169))  # Создаем и отрисовываем кнопку "Назад"

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если событие выхода
                run = False  # Прекращаем выполнение цикла
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                if back_button.collidepoint(event.pos):  # Если нажата кнопка "Назад"
                    run = False  # Прекращаем выполнение цикла

        pygame.display.flip()  # Обновляем экран
