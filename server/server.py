from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple, Dict
from .database import add_session, get_sessions, remove_session

app = FastAPI()

ROWS, COLS = 10, 10


class Ship(BaseModel):
    size: int
    orientation: int  # 0 for horizontal, 1 for vertical
    positions: List[Tuple[int, int]]
    hits: List[Tuple[int, int]] = []

    def is_sunk(self):
        return len(self.hits) == self.size


class Board(BaseModel):
    grid: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]
    ships: List[Ship] = []
    shots: List[Tuple[int, int]] = []

    def place_ship(self, ship: Ship):
        for pos in ship.positions:
            self.grid[pos[0]][pos[1]] = 1
        self.ships.append(ship)

    def can_place(self, ship: Ship):
        for pos in ship.positions:
            if pos[0] >= ROWS or pos[1] >= COLS or self.grid[pos[0]][pos[1]] == 1:
                return False
        return True

    def shoot(self, pos: Tuple[int, int]):
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
    player_name: str = ""


games: Dict[str, Game] = {}


class CreateGameRequest(BaseModel):
    game_id: str
    player_name: str


@app.post("/create_game/")
def create_game(request: CreateGameRequest):
    if request.game_id in games:
        raise HTTPException(status_code=400, detail="Game with this ID already exists.")
    games[request.game_id] = Game(player_name=request.player_name)
    add_session(request.game_id, request.player_name)
    return {"message": "Game created successfully.", "game_id": request.game_id}


@app.get("/get_games/")
def get_games():
    sessions = get_sessions()
    return {"games": sessions}


@app.post("/place_ship/")
def place_ship(ship: Ship, game_id: str, player: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    board = games[game_id].player_board if player == "player" else games[game_id].computer_board
    if board.can_place(ship):
        board.place_ship(ship)
        return {"message": "Ship placed successfully."}
    else:
        raise HTTPException(status_code=400, detail="Cannot place ship here.")


@app.post("/shoot/")
def shoot(pos: Tuple[int, int], game_id: str, player: str):
    if game_id not in games:
        raise HTTPException(status_code=404, detail="Game not found.")
    board = games[game_id].computer_board if player == "player" else games[game_id].player_board
    result = board.shoot(pos)
    return {"result": result}
