from .db import get_db_connection
from typing import List, Dict

def get_games_from_db() -> List[Dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT game_name, logo_url FROM games")
    rows = cursor.fetchall()
    conn.close()
    return [{"game_name": row["game_name"], "logo_url": row["logo_url"]} for row in rows]

def store_games_in_db(games_data: List[Dict]):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM games")
    for game in games_data:
        cursor.execute(
            "INSERT INTO games (game_name, logo_url) VALUES (?, ?)",
            (game["game_name"], game["logo_url"])
        )
    conn.commit()
    conn.close()
