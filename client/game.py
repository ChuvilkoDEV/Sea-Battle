import pygame
import sys
import requests

# Константы и цвета
ROWS, COLS = 10, 10
CELL_SIZE = 20
MARGIN = 150
OFFSET = 0
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (169, 169, 169)

# URL сервера
SERVER_URL = "http://127.0.0.1:8000"


# Псевдо функция для отправки кораблей на сервер
def send_ships_to_server(ships, game_id, player):
    response = requests.post(f"{SERVER_URL}/place_ship/", json={"ships": ships, "game_id": game_id, "player": player})
    return response.json()


def draw_labels(screen):
    font = pygame.font.SysFont('Arial', 24)
    player_label = font.render('Player 1', True, BLACK)
    computer_label = font.render('Player 2', True, BLACK)
    screen.blit(player_label, (MARGIN + 4 * CELL_SIZE, MARGIN - 40))
    screen.blit(computer_label, (MARGIN + 4 * CELL_SIZE + screen.get_width() // 2 + OFFSET // 2, MARGIN - 40))


def draw_grid(screen, shots=None, offset_x=0):
    if shots is None:
        shots = {}
    for row in range(ROWS):
        for col in range(COLS):
            cell_rect = pygame.Rect(MARGIN + col * CELL_SIZE + offset_x, MARGIN + row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRAY, cell_rect, 1)
            if (row, col) in shots:
                if shots[(row, col)] == "hit":
                    pygame.draw.rect(screen, (255, 0, 0), cell_rect)
                elif shots[(row, col)] == "miss":
                    pygame.draw.line(screen, BLACK, cell_rect.topleft, cell_rect.bottomright, 2)
                    pygame.draw.line(screen, BLACK, cell_rect.topright, cell_rect.bottomleft, 2)


def draw_ships(screen, ships, offset_x=0):
    for ship in ships:
        for i in range(ship["size"]):
            pos = (ship["start_pos"][0] + i if ship["orientation"] == 1 else ship["start_pos"][0],
                   ship["start_pos"][1] + i if ship["orientation"] == 0 else ship["start_pos"][1])
            pygame.draw.rect(screen, GRAY, (
                MARGIN + pos[1] * CELL_SIZE + offset_x, MARGIN + pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))


def is_valid_placement(placed_ships, ship_size, orientation, start_pos):
    row, col = start_pos

    # Проверка, чтобы корабль оставался в пределах сетки
    if orientation == 0:  # Горизонтальное размещение
        if col + ship_size > COLS:
            return False
    else:  # Вертикальное размещение
        if row + ship_size > ROWS:
            return False

    # Проверка на перекрытие и соседство с другими кораблями
    for i in range(ship_size):
        if orientation == 0:  # Горизонтальное размещение
            r, c = row, col + i
        else:  # Вертикальное размещение
            r, c = row + i, col

        # Проверка на перекрытие с другими кораблями
        for placed_ship in placed_ships:
            ps_row, ps_col = placed_ship["start_pos"]
            ps_size = placed_ship["size"]
            ps_orientation = placed_ship["orientation"]
            for j in range(ps_size):
                if ps_orientation == 0:
                    pr, pc = ps_row, ps_col + j
                else:
                    pr, pc = ps_row + j, ps_col

                if r == pr and c == pc:
                    return False

        # Проверка на соседство с другими кораблями
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < ROWS and 0 <= nc < COLS:
                    for placed_ship in placed_ships:
                        ps_row, ps_col = placed_ship["start_pos"]
                        ps_size = placed_ship["size"]
                        ps_orientation = placed_ship["orientation"]
                        for j in range(ps_size):
                            if ps_orientation == 0:
                                pr, pc = ps_row, ps_col + j
                            else:
                                pr, pc = ps_row + j, ps_col

                            if nr == pr and nc == pc:
                                return False

    return True


def draw_messages(screen, messages, font, message_box):
    pygame.draw.rect(screen, WHITE, message_box)
    pygame.draw.rect(screen, BLACK, message_box, 1)  # Добавим рамку для области сообщений

    y_offset = message_box.y + 10  # Начинаем с верхней части
    line_spacing = 30

    for message in messages[-1:]:
        words = message.split(' ')
        lines = []
        line = ""
        for word in words:
            if font.size(line + word)[0] < message_box.width - 10:
                line += word + " "
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        for line in lines:
            message_surf = font.render(line, True, BLACK)
            screen.blit(message_surf, (message_box.x + 5, y_offset))
            y_offset += line_spacing


def placement_phase(screen, game_id, player):
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
    messages = ["Разместите корабли."]

    finish_button = pygame.Rect(screen.get_width() - 200, screen.get_height() - 50, 150, 40)
    finish_button_active = False

    message_box = pygame.Rect((screen.get_width() - 150) // 2, MARGIN, 150, 200)
    font = pygame.font.SysFont('Arial', 18)

    while run:
        screen.fill(WHITE)
        draw_labels(screen)
        draw_grid(screen)
        draw_grid(screen, offset_x=screen.get_width() // 2 + OFFSET)

        for i, (size, label) in enumerate(set(ships_to_place)):
            count = ships_to_place.count((size, label))
            font = pygame.font.SysFont('Arial', 24)
            count_label = font.render(str(count), True, BLACK)
            screen.blit(count_label, (10, 100 + i * CELL_SIZE * 2))
            for j in range(size):
                pygame.draw.rect(screen, GRAY, (30 + j * CELL_SIZE, 100 + i * CELL_SIZE * 2, CELL_SIZE, CELL_SIZE))

        pygame.draw.rect(screen, GRAY if not finish_button_active else BLACK, finish_button)
        font = pygame.font.SysFont('Arial', 24)
        finish_label = font.render("Закончить", True, WHITE)
        screen.blit(finish_label, (finish_button.x + 10, finish_button.y + 10))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    orientation = (orientation + 1) % 2
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = event.pos
                if finish_button.collidepoint(event.pos) and finish_button_active:
                    try:
                        response = requests.get(f"{SERVER_URL}/get_game_info/{game_id}")
                        game_info = response.json()
                    except requests.exceptions.JSONDecodeError:
                        messages.append("Ошибка: Неверный ответ от сервера.")
                        game_info = None

                    if game_info and not game_info.get("player2_name"):
                        messages.append("Второй игрок ещё не подключился.")
                        print("Второй игрок ещё не подключился.")
                    else:
                        try:
                            response = send_ships_to_server(placed_ships, game_id, player)
                        except requests.exceptions.JSONDecodeError:
                            messages.append("Ошибка отправки данных на сервер.")
                            print("Ошибка отправки данных на сервер.")
                        else:
                            if response['message'] == "Ship placed successfully.":
                                run = False
                                game_phase(screen, placed_ships, game_id, player)
                            else:
                                messages.append("Ошибка: " + response.get("error", "Неизвестная ошибка"))
                else:
                    ship_index = (mouse_y - 100) // (2 * CELL_SIZE)
                    if 0 <= ship_index < len(ships_to_place):
                        dragging = True
                        ship_pos = (mouse_x, mouse_y)
                        current_ship_index = ship_index
                        current_ship_size = ships_to_place[current_ship_index][0]
            if event.type == pygame.MOUSEBUTTONUP:
                if dragging:
                    mouse_x, mouse_y = event.pos
                    col = (mouse_x - MARGIN) // CELL_SIZE
                    row = (mouse_y - MARGIN) // CELL_SIZE
                    start_pos = (row, col)
                    if is_valid_placement(placed_ships, current_ship_size, orientation, start_pos):
                        placed_ships.append(
                            {"size": current_ship_size, "orientation": orientation, "start_pos": start_pos})
                        ships_to_place.remove((current_ship_size, ships_to_place[current_ship_index][1]))
                        if not ships_to_place:
                            finish_button_active = True
                        else:
                            current_ship_index = 0
                            current_ship_size = ships_to_place[current_ship_index][0]
                            messages.append(f"Корабль {current_ship_size}-клеточный размещен.")
                    else:
                        messages.append("Некорректное размещение.")
                    dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                ship_pos = (event.pos[1] - MARGIN) // CELL_SIZE, (event.pos[0] - MARGIN) // CELL_SIZE

        if dragging:
            draw_ships(screen, [
                {"size": current_ship_size, "orientation": orientation, "start_pos": (ship_pos[0], ship_pos[1])}])

        draw_ships(screen, placed_ships)
        draw_messages(screen, messages, font, message_box)
        pygame.display.flip()


def game_phase(screen, placed_ships, game_id, player):
    run = True
    offset_x = screen.get_width() // 2 + OFFSET
    messages = ["Игра началась. Стреляйте по полю противника."]
    message_box = pygame.Rect((screen.get_width() - 150) // 2, MARGIN, 150, 200)
    font = pygame.font.SysFont('Arial', 18)

    my_shots = {}  # Выстрелы по полю противника
    enemy_shots = {}  # Выстрелы противника по вашему полю

    while run:
        try:
            response = requests.get(f"{SERVER_URL}/get_game_info/{game_id}")
            game_info = response.json()
        except requests.exceptions.JSONDecodeError:
            messages.append("Ошибка: Неверный ответ от сервера.")
            game_info = None

        if not game_info:
            continue

        # Check if 'current_turn' exists in the response
        if 'current_turn' not in game_info:
            messages.append("Ошибка: Неверный формат данных от сервера.")
            pygame.display.flip()
            continue

        current_player = game_info['current_turn']

        screen.fill(WHITE)
        draw_labels(screen)
        draw_grid(screen, my_shots, offset_x)  # Выстрелы игрока на поле противника
        draw_grid(screen, enemy_shots)  # Выстрелы противника на поле игрока

        # Рисуем корабли игрока на его поле, но не на поле противника
        draw_ships(screen, placed_ships)

        draw_messages(screen, messages, font, message_box)

        if current_player != player:
            messages.append("Ожидание хода другого игрока.")
            enemy_shot = game_info.get('last_shot')
            if enemy_shot:
                enemy_shots[(enemy_shot[0], enemy_shot[1])] = "hit" if enemy_shot[2] == "hit" else "miss"
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    if offset_x + MARGIN <= mouse_x < offset_x + MARGIN + COLS * CELL_SIZE and \
                            MARGIN <= mouse_y < MARGIN + ROWS * CELL_SIZE:
                        col = (mouse_x - offset_x - MARGIN) // CELL_SIZE
                        row = (mouse_y - MARGIN) // CELL_SIZE
                        try:
                            response = requests.post(f"{SERVER_URL}/shoot/",
                                                     json={"game_id": game_id, "pos": (row, col),
                                                           "player": current_player})
                            result = response.json()
                        except requests.exceptions.JSONDecodeError:
                            messages.append("Ошибка: Неверный ответ от сервера.")
                            result = None

                        if result:
                            if result.get("result") == "hit":
                                my_shots[(row, col)] = "hit"
                                messages.append(f"Попадание! Ходит {current_player}.")
                            elif result.get("result") == "miss":
                                my_shots[(row, col)] = "miss"
                                messages.append(f"Мимо! Ходит другой игрок.")
                            elif result.get("result") == "sunk":
                                my_shots[(row, col)] = "hit"
                                messages.append(f"Корабль потоплен! Ходит {current_player}.")
                            elif result.get("result") == "already_shot":
                                messages.append("Вы уже стреляли сюда. Ходит другой игрок.")

        pygame.display.flip()
