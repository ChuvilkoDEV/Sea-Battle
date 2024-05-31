import sqlite3

# Настройка подключения к базе данных SQLite
conn = sqlite3.connect('game_sessions.db')
c = conn.cursor()

# Создание таблицы, если она не существует
c.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    game_id TEXT PRIMARY KEY,
    player1_name TEXT,
    player2_name TEXT,
    player1_ships TEXT,
    player2_ships TEXT,
    player1_shots TEXT,
    player2_shots TEXT
)
''')
conn.commit()


def add_session(game_id, player1_name, player2_name=""):
    """
    Добавляет новую игровую сессию в базу данных.

    :param game_id: ID игры
    :param player1_name: Имя первого игрока
    :param player2_name: Имя второго игрока (по умолчанию пустая строка)
    """
    with conn:
        c.execute('''
            INSERT OR REPLACE INTO sessions (
                game_id, player1_name, player2_name, player1_ships, player2_ships, player1_shots, player2_shots
            ) VALUES (?, ?, ?, '', '', '', '')
        ''', (game_id, player1_name, player2_name))


def update_player2(game_id, player2_name):
    """
    Обновляет имя второго игрока в базе данных.

    :param game_id: ID игры
    :param player2_name: Имя второго игрока
    """
    with conn:
        c.execute("UPDATE sessions SET player2_name = ? WHERE game_id = ?", (player2_name, game_id))


def update_ships(game_id, player, ships):
    """
    Обновляет информацию о кораблях игрока в базе данных.

    :param game_id: ID игры
    :param player: Имя игрока ('player1' или 'player2')
    :param ships: Позиции кораблей в формате строки
    """
    column = f"{player}_ships"
    with conn:
        c.execute(f"UPDATE sessions SET {column} = ? WHERE game_id = ?", (ships, game_id))


def update_shots(game_id, player, shots):
    """
    Обновляет информацию о выстрелах игрока в базе данных.

    :param game_id: ID игры
    :param player: Имя игрока ('player1' или 'player2')
    :param shots: Координаты выстрелов в формате строки
    """
    column = f"{player}_shots"
    with conn:
        c.execute(f"UPDATE sessions SET {column} = ? WHERE game_id = ?", (shots, game_id))


def get_sessions():
    """
    Возвращает список всех игровых сессий.

    :return: Список ID всех игровых сессий
    """
    c.execute("SELECT game_id FROM sessions")
    sessions = c.fetchall()
    return [session[0] for session in sessions]


def get_session(game_id):
    """
    Возвращает данные игровой сессии по ее ID.

    :param game_id: ID игры
    :return: Данные игровой сессии в формате словаря
    """
    c.execute("SELECT * FROM sessions WHERE game_id = ?", (game_id,))
    session = c.fetchone()
    if session:
        return {
            "game_id": session[0],
            "player1_name": session[1],
            "player2_name": session[2],
            "player1_ships": session[3],
            "player2_ships": session[4],
            "player1_shots": session[5],
            "player2_shots": session[6]
        }
    return None


def remove_session(game_id):
    """
    Удаляет игровую сессию из базы данных по ее ID.

    :param game_id: ID игры
    """
    with conn:
        c.execute("DELETE FROM sessions WHERE game_id = ?", (game_id,))
