# server/database.py
import redis

# Настройка подключения к Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0)


def add_session(game_id, player_name):
    redis_client.hset(game_id, "player_name", player_name)


def get_sessions():
    sessions = redis_client.keys()
    return [session.decode('utf-8') for session in sessions]


def remove_session(game_id):
    redis_client.delete(game_id)
