import os
import sqlite3
import logging
logger = logging.getLogger(__name__)
UPLOAD_FOLDER = 'static/uploads'
def get_db_connection():
    conn = sqlite3.connect("news.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_name TEXT NOT NULL,
            logo_url TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
 # Create ewc_info table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ewc_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            header TEXT,
            series TEXT,
            organizers TEXT,
            location TEXT,
            prize_pool TEXT,
            start_date TEXT,
            end_date TEXT,
            liquipedia_tier TEXT,
            logo_light TEXT,
            logo_dark TEXT,
            location_logo TEXT,
            social_links TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Create games table (if not already added)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            genre TEXT,
            platform TEXT,
            release_date TEXT,
            description TEXT,
            logo TEXT
        )
    ''')
    # Create teams table (if not already added)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_name TEXT,
            logo_url TEXT
        )
    ''')
    # Create events table (if not already added)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        link TEXT
    )
''')
    # Create matches table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game TEXT,
            match_date TEXT,
            group_name TEXT,
            team1_name TEXT,
            team1_logo TEXT,
            team2_name TEXT,
            team2_logo TEXT,
            match_time TEXT,
            score TEXT
        )
    ''') 
    # Create transfers table
    cursor.execute('''
CREATE TABLE IF NOT EXISTS transfers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unique_id TEXT UNIQUE,
    game TEXT,
    date TEXT,
    player_name TEXT,
    player_flag TEXT,
    old_team_name TEXT,
    old_team_logo_light TEXT,
    old_team_logo_dark TEXT,
    new_team_name TEXT,
    new_team_logo_light TEXT,
    new_team_logo_dark TEXT
)
''')

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news'")
    table_exists = cursor.fetchone()

    if table_exists:
        cursor.execute("PRAGMA table_info(news)")
        columns = {col[1]: col for col in cursor.fetchall()}

        if 'thumbnail_url' not in columns:
            cursor.execute('ALTER TABLE news ADD COLUMN thumbnail_url TEXT')

        if 'id' not in columns or 'AUTOINCREMENT' not in cursor.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='news'"
        ).fetchone()[0]:
            cursor.execute('''
                CREATE TABLE news_temp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    writer TEXT NOT NULL,
                    thumbnail_url TEXT,
                    news_link TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            cursor.execute('''
                INSERT INTO news_temp (id, title, description, writer, thumbnail_url, news_link, created_at, updated_at)
                SELECT id, title, description, writer, thumbnail_url, news_link, created_at, updated_at FROM news
            ''')
            cursor.execute('DROP TABLE news')
            cursor.execute('ALTER TABLE news_temp RENAME TO news')
    else:
        cursor.execute('''
            CREATE TABLE news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                writer TEXT NOT NULL,
                thumbnail_url TEXT,
                news_link TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    conn.close()

def reset_db_sequence():
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sqlite_sequence WHERE name IN ('news', 'teams', 'events', 'ewc_info')")
        conn.commit()
    except sqlite3.Error as e:
        logger.error(f"Failed to reset SQLite sequence: {str(e)}")
        raise
    finally:
        conn.close()