from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Dict
import uuid
from .database import add_session, get_sessions, get_session, update_player2, update_ships, update_shots, remove_session

app = FastAPI()

ROWS, COLS = 10, 10


class Ship(BaseModel):
    size: int
    orientation: int
    positions: List[Tuple[int, int]]
    hits: List[Tuple[int, int]] = []

    def is_sunk(self):
        """Проверяет, потоплен ли корабль на основе количества попаданий."""
        return len(self.hits) == self.size


class Board(BaseModel):
    grid: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    ships: List[Ship] = []
    shots: List[Tuple[int, int]] = []

    def place_ship(self, ship: Ship):
        """Размещает корабль на поле, отмечая его позиции."""
        for pos in ship.positions:
            self.grid[pos[0]][pos[1]] = 1
        self.ships.append(ship)

    def can_place(self, ship: Ship):
        """Проверяет, можно ли разместить корабль на указанных позициях."""
        for pos in ship.positions:
            if pos[0] >= ROWS or pos[1] >= COLS or self.grid[pos[0]][pos[1]] == 1:
                return False
        return True

    def shoot(self, pos: Tuple[int, int]):
        """Выполняет выстрел по указанной позиции и определяет результат."""
        if pos in self.shots:
            return "already_shot"
        self.shots.append(pos)
        for ship in self.ships:
            if pos in ship.positions:
                ship.hits.append(pos)
                if ship.is_sunk():
                    return "sunk"
                return "hit"
        return "miss"


class Game(BaseModel):
    player_board: Board = Board()
    computer_board: Board = Board()
    player1_name: str = ""
    player2_name: str = ""


games: Dict[str, Game] = {}


class CreateGameRequest(BaseModel):
    player1_name: str


class JoinGameRequest(BaseModel):
    game_id: str
    player2_name: str


@app.post("/create_game/")
def create_game(request: CreateGameRequest):
    """Создает новую игровую сессию и возвращает ID игры и имя первого игрока."""
    game_id = str(uuid.uuid4())
    games[game_id] = Game(player1_name=request.player1_name)
    add_session(game_id, request.player1_name)
    return {"message": "Game created successfully.", "game_id": game_id}


@app.post("/join_game/")
def join_game(request: JoinGameRequest):
    """Позволяет второму игроку подключиться к существующей игре."""
    if request.game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    game = games[request.game_id]
    if game.player2_name:
        raise HTTPException(status_code=400, detail="Game already has two players.")
    game.player2_name = request.player2_name
    update_player2(request.game_id, request.player2_name)
    return {"message": "Player 2 joined successfully.", "game_id": request.game_id}


@app.get("/get_games/")
def get_games():
    """Получает список активных игровых сессий."""
    sessions = get_sessions()
    return {"games": sessions}


@app.post("/place_ship/")
def place_ship(ship: Ship, game_id: str, player: str):
    """Размещает корабль на поле указанного игрока."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    board = games[game_id].player_board if player == "player1" else games[game_id].computer_board
    if board.can_place(ship):
        board.place_ship(ship)
        ships_data = [ship.dict() for ship in board.ships]
        update_ships(game_id, player, str(ships_data))
        return {"message": "Ship placed successfully."}
    else:
        raise HTTPException(status_code=400, detail="Cannot place ship here.")


@app.post("/shoot/")
def shoot(pos: Tuple[int, int], game_id: str, player: str):
    """Выполняет выстрел по указанной позиции и возвращает результат."""
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    board = games[game_id].computer_board if player == "player1" else games[game_id].player_board
    result = board.shoot(pos)
    shots_data = board.shots
    update_shots(game_id, player, str(shots_data))
    return {"result": result}
