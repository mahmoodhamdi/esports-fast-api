# app/main.py
from fastapi import FastAPI
from app.routes.ewc_teams import router as teams_router
from app.routes.games import router as games_router
from app.routes.prizes import router as prizes_router
from app.routes.ewc_info import router as info_router
from app.routes.ewc_events import router as events_router
from app.routes.ewc_matches import router as matches_router
from app.db import init_db

app = FastAPI(title="EWC API")

init_db()

app.include_router(teams_router, prefix="/api")
app.include_router(games_router, prefix="/api")
app.include_router(prizes_router, prefix="/api")
app.include_router(info_router, prefix="/api")
app.include_router(events_router, prefix="/api")
app.include_router(matches_router, prefix="/api")
