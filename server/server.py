from fastapi import FastAPI, HTTPException  # Импортируем FastAPI для создания веб-приложения и HTTPException для обработки ошибок
from pydantic import BaseModel  # Импортируем BaseModel из Pydantic для создания моделей данных
from typing import List, Tuple, Dict  # Импортируем типы данных для аннотации типов
from .database import add_session, get_sessions, remove_session  # Импортируем функции для работы с базой данных из локального модуля database

app = FastAPI()  # Создаем экземпляр FastAPI

ROWS, COLS = 10, 10  # Устанавливаем размеры игрового поля (10x10)


class Ship(BaseModel):  # Определяем модель данных для корабля
    size: int  # Размер корабля
    orientation: int  # Ориентация: 0 для горизонтальной, 1 для вертикальной
    positions: List[Tuple[int, int]]  # Список позиций, занимаемых кораблем
    hits: List[Tuple[int, int]] = []  # Список попаданий по кораблю, изначально пуст

    def is_sunk(self):  # Метод для проверки, потоплен ли корабль
        return len(self.hits) == self.size  # Корабль потоплен, если количество попаданий равно его размеру


class Board(BaseModel):  # Определяем модель данных для игрового поля
    grid: List[List[int]] = [[0 for _ in range(COLS)] for _ in range(ROWS)]  # Создаем пустую сетку поля (10x10), заполненную нулями
    ships: List[Ship] = []  # Список кораблей на поле
    shots: List[Tuple[int, int]] = []  # Список выстрелов

    def place_ship(self, ship: Ship):  # Метод для размещения корабля на поле
        for pos in ship.positions:  # Для каждой позиции корабля
            self.grid[pos[0]][pos[1]] = 1  # Обозначаем на сетке, что клетка занята
        self.ships.append(ship)  # Добавляем корабль в список кораблей

    def can_place(self, ship: Ship):  # Метод для проверки, можно ли разместить корабль в указанных позициях
        for pos in ship.positions:  # Для каждой позиции корабля
            if pos[0] >= ROWS or pos[1] >= COLS or self.grid[pos[0]][pos[1]] == 1:  # Если позиция выходит за границы поля или занята
                return False  # Размещение невозможно
        return True  # Размещение возможно

    def shoot(self, pos: Tuple[int, int]):  # Метод для выполнения выстрела по указанной позиции
        if pos in self.shots:  # Если по этой позиции уже стреляли
            return "already_shot"  # Сообщаем, что по этой позиции уже был выстрел
        self.shots.append(pos)  # Добавляем позицию в список выстрелов
        for ship in self.ships:  # Для каждого корабля на поле
            if pos in ship.positions:  # Если по этой позиции находится корабль
                ship.hits.append(pos)  # Добавляем попадание в список попаданий по кораблю
                if ship.is_sunk():  # Если корабль потоплен
                    return "sunk"  # Сообщаем, что корабль потоплен
                return "hit"  # Сообщаем, что был попадание по кораблю
        return "miss"  # Если ни один корабль не был поражен, сообщаем о промахе


class Game(BaseModel):  # Определяем модель данных для игры
    player_board: Board = Board()  # Игровое поле игрока
    computer_board: Board = Board()  # Игровое поле компьютера
    player_name: str = ""  # Имя игрока


games: Dict[str, Game] = {}  # Словарь для хранения игр, где ключ - ID игры, значение - объект Game


class CreateGameRequest(BaseModel):  # Модель данных для запроса на создание игры
    game_id: str  # ID игры
    player_name: str  # Имя игрока


@app.post("/create_game/")  # Эндпоинт для создания новой игры
def create_game(request: CreateGameRequest):  # Обработчик запроса на создание игры
    if request.game_id in games:  # Если игра с таким ID уже существует
        raise HTTPException(status_code=400, detail="Game with this ID already exists.")  # Возвращаем ошибку 400
    games[request.game_id] = Game(player_name=request.player_name)  # Создаем новую игру и добавляем ее в словарь
    add_session(request.game_id, request.player_name)  # Добавляем сессию в базу данных
    return {"message": "Game created successfully.", "game_id": request.game_id}  # Возвращаем сообщение об успешном создании игры


@app.get("/get_games/")  # Эндпоинт для получения списка игр
def get_games():  # Обработчик запроса на получение списка игр
    sessions = get_sessions()  # Получаем список сессий из базы данных
    return {"games": sessions}  # Возвращаем список игр


@app.post("/place_ship/")  # Эндпоинт для размещения корабля на поле
def place_ship(ship: Ship, game_id: str, player: str):  # Обработчик запроса на размещение корабля
    if game_id not in games:  # Если игра с указанным ID не найдена
        raise HTTPException(status_code=404, detail="Game not found.")  # Возвращаем ошибку 404
    board = games[game_id].player_board if player == "player" else games[game_id].computer_board  # Определяем, на чье поле размещать корабль
    if board.can_place(ship):  # Если можно разместить корабль
        board.place_ship(ship)  # Размещаем корабль
        return {"message": "Ship placed successfully."}  # Возвращаем сообщение об успешном размещении корабля
    else:  # Если нельзя разместить корабль
        raise HTTPException(status_code=400, detail="Cannot place ship here.")  # Возвращаем ошибку 400


@app.post("/shoot/")  # Эндпоинт для выполнения выстрела
def shoot(pos: Tuple[int, int], game_id: str, player: str):  # Обработчик запроса на выстрел
    if game_id not in games:  # Если игра с указанным ID не найдена
        raise HTTPException(status_code=404, detail="Game not found.")  # Возвращаем ошибку 404
    board = games[game_id].computer_board if player == "player" else games[game_id].player_board  # Определяем, по чьему полю стреляем
    result = board.shoot(pos)  # Выполняем выстрел
    return {"result": result}  # Возвращаем результат выстрела
