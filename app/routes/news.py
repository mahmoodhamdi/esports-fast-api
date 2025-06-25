from fastapi import APIRouter, File, Form, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
import shutil
import os
import sqlite3
from app.utils import allowed_file, is_valid_thumbnail, is_valid_url
from app.db import reset_db_sequence

router = APIRouter(prefix="/news", tags=["News"])

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@router.post("")
async def create_news(
    title: str = Form(...),
    writer: str = Form(...),
    description: Optional[str] = Form(""),
    thumbnail_url: Optional[str] = Form(""),
    news_link: Optional[str] = Form(""),
    thumbnail_file: Optional[UploadFile] = File(None)
):
    if not title or not writer:
        raise HTTPException(status_code=400, detail="Title and writer are required")

    final_thumbnail_url = ""

    if thumbnail_file:
        if not allowed_file(thumbnail_file.filename):
            raise HTTPException(status_code=400, detail="Invalid file type")
        filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{thumbnail_file.filename}"
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(file_path, "wb") as f:
            shutil.copyfileobj(thumbnail_file.file, f)
        final_thumbnail_url = f"/{UPLOAD_FOLDER}/{filename}"
    elif thumbnail_url:
        if not is_valid_thumbnail(thumbnail_url):
            raise HTTPException(status_code=400, detail="Invalid thumbnail URL")
        final_thumbnail_url = thumbnail_url

    if news_link and not is_valid_url(news_link):
        raise HTTPException(status_code=400, detail="Invalid news link URL")

    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO news (title, description, writer, thumbnail_url, news_link)
            VALUES (?, ?, ?, ?, ?)
        ''', (title[:255], description[:2000], writer[:100], final_thumbnail_url, news_link))
        conn.commit()
        news_id = cursor.lastrowid
        return {"message": "News created successfully", "id": news_id}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.get("")
def get_news(
    page: int = Query(1, gt=0),
    per_page: int = Query(10, gt=0, le=100),
    writer: Optional[str] = None,
    search: Optional[str] = None,
    sort: str = Query("created_at", regex="^(created_at|title)$")
):
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()

        query = '''
            SELECT id, title, description, writer, thumbnail_url, news_link, created_at, updated_at
            FROM news WHERE 1=1
        '''
        params = []

        if writer:
            query += " AND writer LIKE ?"
            params.append(f"%{writer}%")

        if search:
            query += " AND (title LIKE ? OR description LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        query += f" ORDER BY {sort} DESC LIMIT ? OFFSET ?"
        params.extend([per_page, (page - 1) * per_page])
        cursor.execute(query, params)

        news_items = [
            {
                "id": row[0],
                "title": row[1],
                "description": row[2],
                "writer": row[3],
                "thumbnail_url": row[4] or '',
                "news_link": row[5],
                "created_at": row[6],
                "updated_at": row[7],
            }
            for row in cursor.fetchall()
        ]

        # total count
        count_query = 'SELECT COUNT(*) FROM news WHERE 1=1'
        count_params = []

        if writer:
            count_query += " AND writer LIKE ?"
            count_params.append(f"%{writer}%")

        if search:
            count_query += " AND (title LIKE ? OR description LIKE ?)"
            count_params.extend([f"%{search}%", f"%{search}%"])

        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]

        return {
            "news": news_items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page
            }
        }

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.put("/{id}")
async def update_news(
    id: int,
    title: Optional[str] = Form(None),
    writer: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    thumbnail_url: Optional[str] = Form(None),
    news_link: Optional[str] = Form(None),
    thumbnail_file: Optional[UploadFile] = File(None)
):
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM news WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="News item not found")

        final_thumbnail_url = None
        if thumbnail_file:
            if not allowed_file(thumbnail_file.filename):
                raise HTTPException(status_code=400, detail="Invalid file type")
            filename = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{thumbnail_file.filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                shutil.copyfileobj(thumbnail_file.file, f)
            final_thumbnail_url = f"/{UPLOAD_FOLDER}/{filename}"
        elif thumbnail_url:
            if not is_valid_thumbnail(thumbnail_url):
                raise HTTPException(status_code=400, detail="Invalid thumbnail URL")
            final_thumbnail_url = thumbnail_url

        if news_link and not is_valid_url(news_link):
            raise HTTPException(status_code=400, detail="Invalid news link URL")

        update_data = {}
        if title:
            update_data['title'] = title[:255]
        if description:
            update_data['description'] = description[:2000]
        if writer:
            update_data['writer'] = writer[:100]
        if final_thumbnail_url is not None:
            update_data['thumbnail_url'] = final_thumbnail_url
        if news_link:
            update_data['news_link'] = news_link

        if not update_data:
            raise HTTPException(status_code=400, detail="No data provided to update")

        update_data['updated_at'] = datetime.utcnow().isoformat()

        set_clause = ', '.join(f"{k} = ?" for k in update_data.keys())
        values = list(update_data.values()) + [id]

        cursor.execute(f"UPDATE news SET {set_clause} WHERE id = ?", values)
        conn.commit()
        return {"message": "News updated successfully"}

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.delete("/{id}")
def delete_news(id: int):
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM news WHERE id = ?", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="News item not found")
        cursor.execute("DELETE FROM news WHERE id = ?", (id,))
        conn.commit()
        return {"message": "News deleted successfully"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@router.delete("")
def delete_all_news():
    try:
        conn = sqlite3.connect('news.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM news")
        conn.commit()
        reset_db_sequence()
        return {"message": "All news deleted and ID reset"}
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
