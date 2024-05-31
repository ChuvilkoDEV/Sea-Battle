import pygame
import sys
import requests
from utils import draw_button

# Константы и цвета
ROWS, COLS = 10, 10
CELL_SIZE = 20
MARGIN = 100
OFFSET = 50
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)

# URL сервера
SERVER_URL = "http://127.0.0.1:8000"


# Псевдо функция для отправки кораблей на сервер
def send_ships_to_server(ships, game_id, player):
    # В реальной ситуации здесь будет запрос на сервер
    response = requests.post(f"{SERVER_URL}/place_ships/", json={"ships": ships, "game_id": game_id, "player": player})
    return response.json()


def draw_labels(screen):
    font = pygame.font.SysFont('Arial', 24)
    player_label = font.render('Игрок', True, BLACK)
    computer_label = font.render('Компьютер', True, BLACK)
    screen.blit(player_label, (MARGIN + 4 * CELL_SIZE, MARGIN - 40))
    screen.blit(computer_label, (MARGIN + 4 * CELL_SIZE + screen.get_width() // 2 + OFFSET // 2, MARGIN - 40))


def draw_grid(screen, offset_x=0):
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(screen, GRAY,
                             (MARGIN + col * CELL_SIZE + offset_x, MARGIN + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


def draw_ships(screen, ships, offset_x=0):
    for ship in ships:
        for i in range(ship["size"]):
            pos = (ship["start_pos"][0] + i if ship["orientation"] == 1 else ship["start_pos"][0],
                   ship["start_pos"][1] + i if ship["orientation"] == 0 else ship["start_pos"][1])
            pygame.draw.rect(screen, GRAY,
                             (MARGIN + pos[1] * CELL_SIZE + offset_x, MARGIN + pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def is_valid_placement(ships, size, orientation, start_pos):
    row, col = start_pos

    # Проверка на выход за границы поля
    if orientation == 0 and col + size > COLS:
        return False
    if orientation == 1 and row + size > ROWS:
        return False

    # Проверка на соседство с другими кораблями
    for ship in ships:
        for i in range(-1, ship["size"] + 1):
            for j in range(-1, 2):
                if orientation == 0:
                    if (row + j, col + i) in [
                        (ship["start_pos"][0] + k if ship["orientation"] == 1 else ship["start_pos"][0],
                         ship["start_pos"][1] + k if ship["orientation"] == 0 else ship["start_pos"][1]) for k in
                        range(ship["size"])]:
                        return False
                else:
                    if (row + i, col + j) in [
                        (ship["start_pos"][0] + k if ship["orientation"] == 1 else ship["start_pos"][0],
                         ship["start_pos"][1] + k if ship["orientation"] == 0 else ship["start_pos"][1]) for k in
                        range(ship["size"])]:
                        return False
    return True


def draw_remaining_ships(screen, ships_to_place):
    font = pygame.font.SysFont('Arial', 20)
    unique_ships = {}
    for ship in ships_to_place:
        if ship[0] not in unique_ships:
            unique_ships[ship[0]] = 1
        else:
            unique_ships[ship[0]] += 1

    y_offset = 100
    for size, count in sorted(unique_ships.items(), reverse=True):
        count_label = font.render(f'{count}x', True, BLACK)
        screen.blit(count_label, (10, y_offset))
        for j in range(size):
            pygame.draw.rect(screen, GRAY,
                             (40 + j * CELL_SIZE, y_offset, CELL_SIZE, CELL_SIZE))
        y_offset += 2 * CELL_SIZE


def placement_phase(screen, game_id):
    run = True
    orientation = 0
    ships_to_place = [(4, "4-клеточный"), (3, "3-клеточный"), (3, "3-клеточный"),
                      (2, "2-клеточный"), (2, "2-клеточный"), (2, "2-клеточный"),
                      (1, "1-клеточный"), (1, "1-клеточный"), (1, "1-клеточный"), (1, "1-клеточный")]
    current_ship_index = 0
    current_ship_size = ships_to_place[current_ship_index][0]
    dragging = False
    ship_pos = (0, 0)
    placed_ships = []
    finish_button_active = False

    while run:
        screen.fill(WHITE)
        draw_labels(screen)
        draw_grid(screen)
        draw_grid(screen, screen.get_width() // 2 + OFFSET)

        draw_remaining_ships(screen, ships_to_place)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    orientation = (orientation + 1) % 2
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if 40 < mouse_x < 40 + 4 * CELL_SIZE and 100 < mouse_y < 100 + len(ships_to_place) * 2 * CELL_SIZE:
                    ship_index = (mouse_y - 100) // (2 * CELL_SIZE)
                    if 0 <= ship_index < len(ships_to_place):
                        dragging = True
                        ship_pos = (mouse_x, mouse_y)
                        current_ship_index = ship_index
                        current_ship_size = ships_to_place[current_ship_index][0]
            if event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    if MARGIN < mouse_x < MARGIN + COLS * CELL_SIZE and MARGIN < mouse_y < MARGIN + ROWS * CELL_SIZE:
                        col = (mouse_x - MARGIN) // CELL_SIZE
                        row = (mouse_y - MARGIN) // CELL_SIZE
                        if is_valid_placement(placed_ships, current_ship_size, orientation, (row, col)):
                            placed_ships.append(
                                {"size": current_ship_size, "orientation": orientation, "start_pos": (row, col)})
                            ships_to_place.pop(current_ship_index)
                            dragging = False
                            if not ships_to_place:
                                finish_button_active = True
                        else:
                            print("Неправильное размещение корабля. Попробуйте другое место.")
                    dragging = False
            if event.type == pygame.MOUSEMOTION:
                if dragging:
                    ship_pos = event.pos

        if dragging:
            base_row = (ship_pos[1] - MARGIN) // CELL_SIZE
            base_col = (ship_pos[0] - MARGIN) // CELL_SIZE
            for i in range(current_ship_size):
                pos_x = (base_col + i if orientation == 0 else base_col) * CELL_SIZE + MARGIN
                pos_y = (base_row + i if orientation == 1 else base_row) * CELL_SIZE + MARGIN
                pygame.draw.rect(screen, GRAY, (pos_x, pos_y, CELL_SIZE, CELL_SIZE))

        draw_ships(screen, placed_ships)

        finish_button_text = 'Закончить размещение'
        finish_button = pygame.Rect(10, 500, 200, 50)
        pygame.draw.rect(screen, GRAY if finish_button_active else BLACK, finish_button)
        font = pygame.font.SysFont('Arial', 24)
        text_surface = font.render(finish_button_text, True, WHITE)
        screen.blit(text_surface, (20, 510))

        if finish_button_active and pygame.mouse.get_pressed()[0]:
            if finish_button.collidepoint(pygame.mouse.get_pos()):
                run = False

        pygame.display.flip()

    if finish_button_active:
        # Отправка всех кораблей на сервер
        response = send_ships_to_server(placed_ships, game_id, "player")
        if response.get("success"):
            game_phase(screen, game_id)
        else:
            print("Ошибка отправки данных на сервер.")
            pygame.quit()
            sys.exit()


def game_phase(screen, game_id):
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
                if MARGIN + screen.get_width() // 2 + OFFSET < mouse_x < MARGIN + screen.get_width() // 2 + OFFSET + COLS * CELL_SIZE and MARGIN < mouse_y < MARGIN + ROWS * CELL_SIZE:
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

