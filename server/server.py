from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Tuple

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


game = Game()


@app.post("/place_ship/")
def place_ship(ship: Ship, player: str):
    board = game.player_board if player == "player" else game.computer_board
    if board.can_place(ship):
        board.place_ship(ship)
        return {"message": "Ship placed successfully."}
    else:
        raise HTTPException(status_code=400, detail="Cannot place ship here.")


@app.post("/shoot/")
def shoot(pos: Tuple[int, int], player: str):
    board = game.computer_board if player == "player" else game.player_board
    result = board.shoot(pos)
    return {"result": result}
