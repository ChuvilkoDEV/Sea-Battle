# server/database.py
import sqlite3

# Настройка подключения к базе данных SQLite
conn = sqlite3.connect('game_sessions.db')
c = conn.cursor()

# Создание таблицы, если она не существует
c.execute('''
CREATE TABLE IF NOT EXISTS sessions (
    game_id TEXT PRIMARY KEY,
    player_name TEXT
)
''')
conn.commit()


def add_session(game_id, player_name):
    with conn:
        c.execute("INSERT OR REPLACE INTO sessions (game_id, player_name) VALUES (?, ?)", (game_id, player_name))


def get_sessions():
    c.execute("SELECT game_id FROM sessions")
    sessions = c.fetchall()
    return [session[0] for session in sessions]


def remove_session(game_id):
    with conn:
        c.execute("DELETE FROM sessions WHERE game_id = ?", (game_id,))
