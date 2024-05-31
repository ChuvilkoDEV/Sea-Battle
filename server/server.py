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
    player_board: Board = Board()
    computer_board: Board = Board()
    player1_name: str = ""
    player2_name: str = ""


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
    board = games[request.game_id].player_board if request.player == "player1" else games[
        request.game_id].computer_board
    for ship_data in request.ships:
        ship = Ship(size=ship_data["size"], orientation=ship_data["orientation"],
                    positions=[
                        (ship_data["start_pos"][0] + i if ship_data["orientation"] == 1 else ship_data["start_pos"][0],
                         ship_data["start_pos"][1] + i if ship_data["orientation"] == 0 else ship_data["start_pos"][1])
                        for i in range(ship_data["size"])])
        if board.can_place(ship):
            board.place_ship(ship)
        else:
            raise HTTPException(status_code=400, detail="Cannot place ship here.")
    return {"message": "Ship placed successfully."}


@app.post("/shoot/")
def shoot(pos: Tuple[int, int], game_id: int, player: str):
    """Выполняет выстрел по указанной позиции и возвращает результат."""
    if game_id >= len(games):
        raise HTTPException(status_code=404, detail="Game not found.")
    board = games[game_id].computer_board if player == "player1" else games[game_id].player_board
    result = board.shoot(pos)
    return {"result": result}
