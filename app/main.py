from fastapi import FastAPI
from app.routes.games import router as games_router
from app.routes.prizes import router as prizes
from app.db import init_db

app = FastAPI(title="EWC Games API")

init_db()  # ← إنشاء الجداول عند بدء التطبيق

app.include_router(games_router, prefix="/api", tags=["Games"])
app.include_router(prizes, prefix="/api", tags=["Prize"])
