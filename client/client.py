import pygame
import sys
import requests
from random import randint

# Инициализация Pygame
pygame.init()

# Определение размеров окна и других параметров
WIDTH, HEIGHT = 900, 600
ROWS, COLS = 10, 10
CELL_SIZE = 40
MARGIN = 50
OFFSET = 200  # Расстояние между полями

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GRAY = (169, 169, 169)
DARKGRAY = (100, 100, 100)

# Создание окна
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Морской бой")

# URL сервера
SERVER_URL = "http://127.0.0.1:8000"


def place_ship(size, orientation, start_pos, player):
    ship = {
        "size": size,
        "orientation": orientation,
        "positions": [(start_pos[0] + i if orientation == 1 else start_pos[0],
                       start_pos[1] + i if orientation == 0 else start_pos[1]) for i in range(size)]
    }
    response = requests.post(f"{SERVER_URL}/place_ship/", json={"ship": ship, "player": player})
    return response.json()


def shoot(pos, player):
    response = requests.post(f"{SERVER_URL}/shoot/", json={"pos": pos, "player": player})
    return response.json()


def draw_labels():
    font = pygame.font.SysFont('Arial', 24)
    player_label = font.render('Игрок', True, BLACK)
    computer_label = font.render('Компьютер', True, BLACK)
    WIN.blit(player_label, (MARGIN + 4 * CELL_SIZE, MARGIN - 40))
    WIN.blit(computer_label, (MARGIN + 4 * CELL_SIZE + WIDTH // 2 + OFFSET // 2, MARGIN - 40))


def draw_grid(offset_x=0):
    for row in range(ROWS):
        for col in range(COLS):
            pygame.draw.rect(WIN, GRAY,
                             (MARGIN + col * CELL_SIZE + offset_x, MARGIN + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)


def draw_button(text, rect, color):
    pygame.draw.rect(WIN, color, rect)
    font = pygame.font.SysFont('Arial', 30)
    label = font.render(text, True, BLACK)
    label_rect = label.get_rect(center=(rect[0] + rect[2] // 2, rect[1] + rect[3] // 2))
    WIN.blit(label, label_rect)


def main_menu():
    run = True
    while run:
        WIN.fill(WHITE)

        play_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 150, 200, 50)
        settings_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 - 50, 200, 50)
        quit_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

        draw_button("Играть", play_button, GRAY)
        draw_button("Настройки", settings_button, GRAY)
        draw_button("Выйти", quit_button, GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    game_loop()
                if settings_button.collidepoint(event.pos):
                    settings_menu()
                if quit_button.collidepoint(event.pos):
                    run = False

        pygame.display.flip()
    pygame.quit()
    sys.exit()


def settings_menu():
    run = True
    while run:
        WIN.fill(WHITE)
        font = pygame.font.SysFont('Arial', 50)
        label = font.render('Настройки', True, BLACK)
        label_rect = label.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))
        WIN.blit(label, label_rect)

        back_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 200, 200, 50)
        draw_button("Назад", back_button, GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    run = False

        pygame.display.flip()


def game_loop():
    run = True
    clock = pygame.time.Clock()
    player_turn = True

    while run:
        clock.tick(60)
        WIN.fill(WHITE)
        draw_labels()

        draw_grid()
        draw_grid(WIDTH // 2 + OFFSET)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN and player_turn:
                mouse_x, mouse_y = event.pos
                if mouse_x > MARGIN + WIDTH // 2 + OFFSET and mouse_y > MARGIN and mouse_x < MARGIN + WIDTH // 2 + OFFSET + COLS * CELL_SIZE and mouse_y < MARGIN + ROWS * CELL_SIZE:
                    col = (mouse_x - MARGIN - WIDTH // 2 - OFFSET) // CELL_SIZE
                    row = (mouse_y - MARGIN) // CELL_SIZE
                    result = shoot((row, col), "player")
                    if result["result"] in ["hit", "sunk"]:
                        print(f"Player hit at {(row, col)}!")
                    elif result["result"] == "miss":
                        print(f"Player missed at {(row, col)}.")
                        player_turn = False

        if not player_turn:
            row, col = randint(0, ROWS - 1), randint(0, COLS - 1)
            result = shoot((row, col), "computer")
            if result["result"] in ["hit", "sunk"]:
                print(f"Computer hit at {(row, col)}!")
            elif result["result"] == "miss":
                print(f"Computer missed at {(row, col)}.")
                player_turn = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main_menu()
