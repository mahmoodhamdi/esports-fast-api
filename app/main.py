from fastapi import FastAPI
from app.routes.games import router as games_router
from app.db import init_db

app = FastAPI(title="EWC Games API")

init_db()  # ← إنشاء الجداول عند بدء التطبيق

app.include_router(games_router, prefix="/api")
