import sqlite3
from contextlib import contextmanager


@contextmanager
def get_db_connection():
    conn = sqlite3.connect('game_sessions.db')
    try:
        yield conn
    finally:
        conn.close()


# Создание таблицы, если она не существует
with get_db_connection() as conn:
    c = conn.cursor()
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
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO sessions (
                game_id, player1_name, player2_name, player1_ships, player2_ships, player1_shots, player2_shots
            ) VALUES (?, ?, ?, '', '', '', '')
        ''', (game_id, player1_name, player2_name))
        conn.commit()


def update_player2(game_id, player2_name):
    """
    Обновляет имя второго игрока в базе данных.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("UPDATE sessions SET player2_name = ? WHERE game_id = ?", (player2_name, game_id))
        conn.commit()


def update_ships(game_id, player, ships):
    """
    Обновляет информацию о кораблях игрока в базе данных.
    """
    column = f"{player}_ships"
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(f"UPDATE sessions SET {column} = ? WHERE game_id = ?", (ships, game_id))
        conn.commit()


def update_shots(game_id, player, shots):
    """
    Обновляет информацию о выстрелах игрока в базе данных.
    """
    column = f"{player}_shots"
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute(f"UPDATE sessions SET {column} = ? WHERE game_id = ?", (shots, game_id))
        conn.commit()


def get_sessions():
    """
    Возвращает список всех игровых сессий.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT game_id FROM sessions")
        sessions = c.fetchall()
        return [session[0] for session in sessions]


def get_session(game_id):
    """
    Возвращает данные игровой сессии по ее ID.
    """
    with get_db_connection() as conn:
        c = conn.cursor()
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
    """
    with get_db_connection() as conn:
        c = conn.cursor()
        c.execute("DELETE FROM sessions WHERE game_id = ?", (game_id,))
        conn.commit()
