from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Dict

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
    player1_board: Board = Board()
    player2_board: Board = Board()
    player1_name: str = ""
    player2_name: str = ""
    current_turn: str = "player1"  # "player1" или "player2"

    def switch_turn(self):
        """Меняет текущего игрока."""
        self.current_turn = "player1" if self.current_turn == "player2" else "player2"


games: List[Game] = []


class CreateGameRequest(BaseModel):
    player1_name: str


class JoinGameRequest(BaseModel):
    game_id: int
    player2_name: str


class PlaceShipsRequest(BaseModel):
    ships: List[Dict]
    game_id: int
    player: str


@app.post("/create_game/")
def create_game(request: CreateGameRequest):
    """Создает новую игровую сессию и возвращает ID игры и имя первого игрока."""
    game_id = len(games)
    games.append(Game(player1_name=request.player1_name))
    return {"message": "Game created successfully.", "game_id": game_id, "player": "player1"}


@app.post("/join_game/")
def join_game(request: JoinGameRequest):
    """Позволяет второму игроку подключиться к существующей игре."""
    if request.game_id >= len(games):
        raise HTTPException(status_code=404, detail="Game not found.")
    game = games[request.game_id]
    if game.player2_name:
        raise HTTPException(status_code=400, detail="Game already has two players.")
    game.player2_name = request.player2_name
    return {"message": "Player 2 joined successfully.", "game_id": request.game_id, "player": "player2"}


@app.get("/get_games/")
def get_games():
    """Получает список активных игровых сессий."""
    return {"games": list(range(len(games)))}


@app.post("/place_ship/")
def place_ship(request: PlaceShipsRequest):
    """Размещает корабли на поле указанного игрока."""
    if request.game_id >= len(games):
        raise HTTPException(status_code=404, detail="Game not found.")
    game = games[request.game_id]
    board = game.player1_board if request.player == "player1" else game.player2_board
    for ship_data in request.ships:
        ship = Ship(
            size=ship_data["size"],
            orientation=ship_data["orientation"],
            positions=[
                (ship_data["start_pos"][0] + i if ship_data["orientation"] == 1 else ship_data["start_pos"][0],
                 ship_data["start_pos"][1] + i if ship_data["orientation"] == 0 else ship_data["start_pos"][1])
                for i in range(ship_data["size"])
            ]
        )
        if board.can_place(ship):
            board.place_ship(ship)
        else:
            raise HTTPException(status_code=400, detail="Cannot place ship here.")
    return {"message": "Ship placed successfully."}


class ShootRequest(BaseModel):
    game_id: int
    pos: Tuple[int, int]
    player: str


@app.post("/shoot/")
def shoot(request: ShootRequest):
    """Выполняет выстрел по указанной позиции и возвращает результат."""
    if request.game_id >= len(games):
        raise HTTPException(status_code=404, detail="Game not found.")
    game = games[request.game_id]
    if game.current_turn != request.player:
        raise HTTPException(status_code=400, detail="Not your turn.")
    board = game.player2_board if request.player == "player1" else game.player1_board
    result = board.shoot(request.pos)

    # Переключение хода только при промахе
    if result == "miss":
        game.switch_turn()

    return {"result": result}


@app.get("/get_game_info/{game_id}")
def get_game_info(game_id: int):
    if game_id >= len(games):
        raise HTTPException(status_code=404, detail="Game not found.")
    game = games[game_id]

    last_shot = None
    if game.current_turn == "player2" and game.player1_board.shots:
        last_shot = game.player1_board.shots[-1]
    elif game.current_turn == "player1" and game.player2_board.shots:
        last_shot = game.player2_board.shots[-1]

    result = None
    if last_shot:
        for ship in (game.player1_board.ships if game.current_turn == "player2" else game.player2_board.ships):
            if last_shot in ship.positions:
                result = "hit" if last_shot in ship.hits else "miss"
                break

    return {
        "player1_name": game.player1_name,
        "player2_name": game.player2_name,
        "current_turn": game.current_turn,
        "last_shot": (last_shot[0], last_shot[1], result) if last_shot else None
    }
