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
    ship = {
        "size": size,
        "orientation": orientation,
        "positions": [(start_pos[0] + i if orientation == 1 else start_pos[0],
                       start_pos[1] + i if orientation == 0 else start_pos[1]) for i in range(size)]
    }
    response = requests.post(f"{SERVER_URL}/place_ship/", json={"ship": ship, "game_id": game_id, "player": player})
    return response.json()


def shoot(pos, game_id, player):
    response = requests.post(f"{SERVER_URL}/shoot/", json={"pos": pos, "game_id": game_id, "player": player})
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


def game_loop(screen, game_id):
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
            row, col = randint(0, ROWS - 1), randint(0, COLS - 1)
            result = shoot((row, col), game_id, "computer")
            if result["result"] in ["hit", "sunk"]:
                print(f"Computer hit at {(row, col)}!")
            elif result["result"] == "miss":
                print(f"Computer missed at {(row, col)}.")
                player_turn = True

        pygame.display.flip()

    pygame.quit()
    sys.exit()
