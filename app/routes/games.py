from fastapi import APIRouter, Query
from typing import List
from app.models import Game
from app.crud import get_games_from_db, store_games_in_db
from app.liquipedia import fetch_ewc_games_from_web

router = APIRouter()

@router.get("/ewc_games", response_model=List[Game])
def get_ewc_games(live: bool = Query(False, description="If true, fetch from Liquipedia and refresh DB")):
    data = []

    if not live:
        data = get_games_from_db()
        if not data:
            # fallback to live if db is empty
            data = fetch_ewc_games_from_web()
            if data:
                store_games_in_db(data)
    else:
        data = fetch_ewc_games_from_web()
        if data:
            store_games_in_db(data)

    return data
