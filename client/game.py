import pygame  # Импортируем модуль Pygame для работы с графикой и игровым циклом
import sys  # Импортируем модуль sys для выхода из программы
import requests  # Импортируем модуль requests для выполнения HTTP-запросов
from random import randint  # Импортируем функцию randint для генерации случайных чисел
from utils import draw_button  # Импортируем функцию draw_button из модуля utils для отрисовки кнопок

# Константы и цвета
ROWS, COLS = 10, 10  # Количество строк и столбцов в сетке
CELL_SIZE = 40  # Размер ячейки
MARGIN = 50  # Отступ от края экрана до сетки
OFFSET = 200  # Смещение между сетками игрока и компьютера
WHITE = (255, 255, 255)  # Цвет белый (RGB)
BLACK = (0, 0, 0)  # Цвет черный (RGB)
GRAY = (169, 169, 169)  # Цвет серый (RGB)

# URL сервера
SERVER_URL = "http://127.0.0.1:8000"  # Устанавливаем URL сервера для API-запросов


def place_ship(size, orientation, start_pos, game_id, player):  # Функция для размещения корабля
    ship = {
        "size": size,  # Размер корабля
        "orientation": orientation,  # Ориентация корабля (горизонтальная или вертикальная)
        "positions": [(start_pos[0] + i if orientation == 1 else start_pos[0],  # Позиции корабля на сетке
                       start_pos[1] + i if orientation == 0 else start_pos[1]) for i in range(size)]
    }
    # Выполняем POST-запрос для размещения корабля
    response = requests.post(f"{SERVER_URL}/place_ship/", json={"ship": ship, "game_id": game_id, "player": player})
    return response.json()  # Возвращаем ответ сервера в формате JSON


def shoot(pos, game_id, player):  # Функция для выполнения выстрела
    # Выполняем POST-запрос для выстрела
    response = requests.post(f"{SERVER_URL}/shoot/", json={"pos": pos, "game_id": game_id, "player": player})
    return response.json()  # Возвращаем ответ сервера в формате JSON


def draw_labels(screen):  # Функция для отрисовки меток на экране
    font = pygame.font.SysFont('Arial', 24)  # Устанавливаем шрифт
    player_label = font.render('Игрок', True, BLACK)  # Рендерим текст "Игрок"
    computer_label = font.render('Компьютер', True, BLACK)  # Рендерим текст "Компьютер"
    screen.blit(player_label, (MARGIN + 4 * CELL_SIZE, MARGIN - 40))  # Отображаем текст "Игрок" на экране
    screen.blit(computer_label, (MARGIN + 4 * CELL_SIZE + screen.get_width() // 2 + OFFSET // 2, MARGIN - 40))  # Отображаем текст "Компьютер" на экране


def draw_grid(screen, offset_x=0):  # Функция для отрисовки сетки
    for row in range(ROWS):  # Для каждой строки
        for col in range(COLS):  # Для каждого столбца
            # Отрисовываем ячейку сетки
            pygame.draw.rect(screen, GRAY,
                             (MARGIN + col * CELL_SIZE + offset_x, MARGIN + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


def placement_phase(screen, game_id):  # Функция для фазы размещения кораблей
    run = True  # Устанавливаем флаг выполнения цикла
    orientation = 0  # Ориентация корабля: 0 - горизонтальная, 1 - вертикальная
    current_ship_size = 4  # Начальный размер корабля
    placed_ships = []  # Список размещенных кораблей

    while run and current_ship_size > 0:  # Запускаем цикл размещения кораблей
        screen.fill(WHITE)  # Заполняем экран белым цветом
        draw_labels(screen)  # Отрисовываем метки
        draw_grid(screen)  # Отрисовываем сетку игрока
        draw_grid(screen, screen.get_width() // 2 + OFFSET)  # Отрисовываем сетку компьютера

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если событие выхода
                run = False  # Прекращаем выполнение цикла
            if event.type == pygame.KEYDOWN:  # Если нажата клавиша
                if event.key == pygame.K_r:  # Если нажата клавиша 'R'
                    orientation = (orientation + 1) % 2  # Меняем ориентацию корабля
            if event.type == pygame.MOUSEBUTTONDOWN:  # Если нажата кнопка мыши
                mouse_x, mouse_y = event.pos  # Получаем координаты мыши
                if mouse_x > MARGIN and mouse_x < MARGIN + COLS * CELL_SIZE and mouse_y > MARGIN and mouse_y < MARGIN + ROWS * CELL_SIZE:
                    col = (mouse_x - MARGIN) // CELL_SIZE  # Вычисляем столбец
                    row = (mouse_y - MARGIN) // CELL_SIZE  # Вычисляем строку
                    response = place_ship(current_ship_size, orientation, (row, col), game_id, "player")  # Размещаем корабль
                    if response.get("success"):  # Если размещение успешно
                        placed_ships.append((current_ship_size, orientation, (row, col)))  # Добавляем корабль в список размещенных
                        current_ship_size -= 1  # Уменьшаем размер следующего корабля

        for ship in placed_ships:  # Для каждого размещенного корабля
            for i in range(ship[0]):  # Для каждой позиции корабля
                pos = (ship[2][0] + i if ship[1] == 1 else ship[2][0],  # Вычисляем позицию ячейки корабля
                       ship[2][1] + i if ship[1] == 0 else ship[2][1])
                pygame.draw.rect(screen, GRAY,  # Отрисовываем ячейку корабля
                                 (MARGIN + pos[1] * CELL_SIZE, MARGIN + pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()  # Обновляем экран

    game_phase(screen, game_id)  # Переходим к фазе игры


def game_phase(screen, game_id):  # Функция для фазы игры
    run = True  # Устанавливаем флаг выполнения цикла
    clock = pygame.time.Clock()  # Создаем объект Clock для управления частотой кадров
    player_turn = True  # Устанавливаем флаг хода игрока

    while run:  # Запускаем игровой цикл
        clock.tick(60)  # Ограничиваем частоту кадров до 60 в секунду
        screen.fill(WHITE)  # Заполняем экран белым цветом
        draw_labels(screen)  # Отрисовываем метки
        draw_grid(screen)  # Отрисовываем сетку игрока
        draw_grid(screen, screen.get_width() // 2 + OFFSET)  # Отрисовываем сетку компьютера

        for event in pygame.event.get():  # Обрабатываем события
            if event.type == pygame.QUIT:  # Если событие выхода
                run = False  # Прекращаем выполнение цикла
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:  # Если нажата кнопка мыши и сейчас ход игрока
                mouse_x, mouse_y = event.pos  # Получаем координаты мыши
                if mouse_x > MARGIN + screen.get_width() // 2 + OFFSET and mouse_y > MARGIN and mouse_x < MARGIN + screen.get_width() // 2 + OFFSET + COLS * CELL_SIZE and mouse_y < MARGIN + ROWS * CELL_SIZE:
                    col = (mouse_x - MARGIN - screen.get_width() // 2 - OFFSET) // CELL_SIZE  # Вычисляем столбец
                    row = (mouse_y - MARGIN) // CELL_SIZE  # Вычисляем строку
                    result = shoot((row, col), game_id, "player")  # Выполняем выстрел и получаем результат
                    if result["result"] in ["hit", "sunk"]:  # Если попадание или потопление
                        print(f"Player hit at {(row, col)}!")  # Выводим сообщение о попадании
                    elif result["result"] == "miss":  # Если промах
                        print(f"Player missed at {(row, col)}.")  # Выводим сообщение о промахе
                        player_turn = False  # Переход хода к компьютеру

        if not player_turn:  # Если сейчас ход компьютера
            row, col = randint(0, ROWS - 1), randint(0, COLS - 1)  # Генерируем случайные координаты выстрела
            result = shoot((row, col), game_id, "computer")  # Выполняем выстрел и получаем результат
            if result["result"] in ["hit", "sunk"]:  # Если попадание или потопление
                print(f"Computer hit at {(row, col)}!")  # Выводим сообщение о попадании
            elif result["result"] == "miss":  # Если промах
                print(f"Computer missed at {(row, col)}.")  # Выводим сообщение о промахе
                player_turn = True  # Переход хода к игроку

        pygame.display.flip()  # Обновляем экран

    pygame.quit()  # Выходим из Pygame
    sys.exit()  # Выходим из программы


def main():  # Главная функция
    pygame.init()  # Инициализируем Pygame
    screen = pygame.display.set_mode((1000, 600))  # Создаем окно
    pygame.display.set_caption('Морской бой')  # Устанавливаем заголовок окна

    game_id = "12345"  # Идентификатор игры (для примера)
    placement_phase(screen, game_id)  # Запускаем фазу размещения кораблей


if __name__ == "__main__":  # Если модуль запущен как основной
    main()  # Вызываем главную функцию
