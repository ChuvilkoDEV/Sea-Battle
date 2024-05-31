import pygame
import sys
import requests
from random import randint
from utils import draw_button

# Константы и цвета
ROWS, COLS = 10, 10
CELL_SIZE = 40
MARGIN = 50
OFFSET = 200
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)

# URL сервера
SERVER_URL = "http://127.0.0.1:8000"


def place_ship(size, orientation, start_pos, game_id, player):
    """
    Размещает корабль на сервере.

    Аргументы:
    size -- размер корабля
    orientation -- ориентация корабля (0 для горизонтальной, 1 для вертикальной)
    start_pos -- начальная позиция корабля (кортеж (строка, столбец))
    game_id -- идентификатор игры
    player -- игрок, который размещает корабль ("player" или "computer")

    Возвращает:
    JSON-ответ от сервера с результатом размещения.
    """
    ship = {
        "size": size,
        "orientation": orientation,
        "positions": [(start_pos[0] + i if orientation == 1 else start_pos[0],
                       start_pos[1] + i if orientation == 0 else start_pos[1]) for i in range(size)]
    }
    response = requests.post(f"{SERVER_URL}/place_ship/", json={"ship": ship, "game_id": game_id, "player": player})
    return response.json()


def shoot(pos, game_id, player):
    """
    Выполняет выстрел по указанной позиции на сервере.

    Аргументы:
    pos -- позиция выстрела (кортеж (строка, столбец))
    game_id -- идентификатор игры
    player -- игрок, который стреляет ("player" или "computer")

    Возвращает:
    JSON-ответ от сервера с результатом выстрела.
    """
    response = requests.post(f"{SERVER_URL}/shoot/", json={"pos": pos, "game_id": game_id, "player": player})
    return response.json()


def get_enemy_shot(game_id, player):
    """
    Получает информацию о выстреле противника с сервера.

    Аргументы:
    game_id -- идентификатор игры
    player -- игрок, для которого запрашивается информация о выстреле противника

    Возвращает:
    JSON-ответ от сервера с информацией о выстреле противника.
    """
    response = requests.get(f"{SERVER_URL}/get_enemy_shot/", params={"game_id": game_id, "player": player})
    return response.json()


def draw_labels(screen):
    """
    Отрисовывает метки на экране (названия игроков).

    Аргументы:
    screen -- объект Pygame Surface, на котором происходит отрисовка
    """
    font = pygame.font.SysFont('Arial', 24)
    player_label = font.render('Игрок', True, BLACK)
    computer_label = font.render('Компьютер', True, BLACK)
    screen.blit(player_label, (MARGIN + 4 * CELL_SIZE, MARGIN - 40))
    screen.blit(computer_label, (MARGIN + 4 * CELL_SIZE + screen.get_width() // 2 + OFFSET // 2, MARGIN - 40))


def draw_grid(screen, offset_x=0):
    """
    Отрисовывает сетку на экране.

    Аргументы:
    screen -- объект Pygame Surface, на котором происходит отрисовка
    offset_x -- горизонтальное смещение сетки
    """
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(screen, GRAY,
                             (MARGIN + col * CELL_SIZE + offset_x, MARGIN + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


def placement_phase(screen, game_id):
    """
    Обрабатывает фазу размещения кораблей игроком.

    Аргументы:
    screen -- объект Pygame Surface, на котором происходит отрисовка
    game_id -- идентификатор игры
    """
    run = True
    orientation = 0
    current_ship_size = 4
    placed_ships = []

    while run and current_ship_size > 0:
        screen.fill(WHITE)
        draw_labels(screen)
        draw_grid(screen)
        draw_grid(screen, screen.get_width() // 2 + OFFSET)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    orientation = (orientation + 1) % 2
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if mouse_x > MARGIN and mouse_x < MARGIN + COLS * CELL_SIZE and mouse_y > MARGIN and mouse_y < MARGIN + ROWS * CELL_SIZE:
                    col = (mouse_x - MARGIN) // CELL_SIZE
                    row = (mouse_y - MARGIN) // CELL_SIZE
                    response = place_ship(current_ship_size, orientation, (row, col), game_id, "player")
                    if response.get("success"):
                        placed_ships.append((current_ship_size, orientation, (row, col)))
                        current_ship_size -= 1

        for ship in placed_ships:
            for i in range(ship[0]):
                pos = (ship[2][0] + i if ship[1] == 1 else ship[2][0],
                       ship[2][1] + i if ship[1] == 0 else ship[2][1])
                pygame.draw.rect(screen, GRAY,
                                 (MARGIN + pos[1] * CELL_SIZE, MARGIN + pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        pygame.display.flip()

    game_phase(screen, game_id)


def game_phase(screen, game_id):
    """
    Обрабатывает фазу игры, включая ходы игрока и компьютера.

    Аргументы:
    screen -- объект Pygame Surface, на котором происходит отрисовка
    game_id -- идентификатор игры
    """
    run = True
    clock = pygame.time.Clock()
    player_turn = True

    while run:
        clock.tick(60)
        screen.fill(WHITE)
        draw_labels(screen)
        draw_grid(screen)
        draw_grid(screen, screen.get_width() // 2 + OFFSET)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                mouse_x, mouse_y = event.pos
                if mouse_x > MARGIN + screen.get_width() // 2 + OFFSET and mouse_y > MARGIN and mouse_x < MARGIN + screen.get_width() // 2 + OFFSET + COLS * CELL_SIZE and mouse_y < MARGIN + ROWS * CELL_SIZE:
                    col = (mouse_x - MARGIN - screen.get_width() // 2 - OFFSET) // CELL_SIZE
                    row = (mouse_y - MARGIN) // CELL_SIZE
                    result = shoot((row, col), game_id, "player")
                    if result["result"] in ["hit", "sunk"]:
                        print(f"Player hit at {(row, col)}!")
                    elif result["result"] == "miss":
                        print(f"Player missed at {(row, col)}.")
                        player_turn = False

        if not player_turn:
            enemy_shot_result = get_enemy_shot(game_id, "player")
            if enemy_shot_result["success"]:
                enemy_shot = enemy_shot_result["shot"]
                row, col = enemy_shot["row"], enemy_shot["col"]
                if enemy_shot["result"] in ["hit", "sunk"]:
                    print(f"Computer hit at {(row, col)}!")
                elif enemy_shot["result"] == "miss":
                    print(f"Computer missed at {(row, col)}.")
                    player_turn = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()
