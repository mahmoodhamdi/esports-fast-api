import os
import sqlite3
from fastapi import UploadFile
from datetime import datetime
from app.utils import UPLOAD_FOLDER

def insert_news(title, writer, description, thumbnail_url, news_link):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news (title, description, writer, thumbnail_url, news_link)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, description, writer, thumbnail_url, news_link))
    conn.commit()
    news_id = cursor.lastrowid
    conn.close()
    return news_id

def fetch_news(page, per_page, writer=None, search=None, sort='created_at'):
    offset = (page - 1) * per_page
    conn = sqlite3.connect('news.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    query = 'SELECT * FROM news WHERE 1=1'
    params = []

    if writer:
        query += ' AND writer LIKE ?'
        params.append(f'%{writer}%')
    if search:
        query += ' AND (title LIKE ? OR description LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%'])

    query += f' ORDER BY {sort} DESC LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    cursor.execute(query, params)

    results = [dict(row) for row in cursor.fetchall()]

    # count
    count_query = 'SELECT COUNT(*) FROM news WHERE 1=1'
    count_params = []
    if writer:
        count_query += ' AND writer LIKE ?'
        count_params.append(f'%{writer}%')
    if search:
        count_query += ' AND (title LIKE ? OR description LIKE ?)'
        count_params.extend([f'%{search}%', f'%{search}%'])
    cursor.execute(count_query, count_params)
    total = cursor.fetchone()[0]

    conn.close()
    return results, total

def update_news_db(id, fields: dict):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    set_clause = ', '.join(f'{k} = ?' for k in fields.keys())
    values = list(fields.values()) + [id]
    query = f'UPDATE news SET {set_clause} WHERE id = ?'
    cursor.execute(query, values)
    conn.commit()
    conn.close()

def delete_news_by_id(id):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM news WHERE id = ?', (id,))
    conn.commit()
    conn.close()

def delete_all_news():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM news')
    conn.commit()
    conn.close()
