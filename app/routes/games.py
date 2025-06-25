from fastapi import APIRouter, Query
from typing import List
from app.models import Game
from app.crud import get_games_from_db, store_games_in_db
from app.liquipedia import fetch_ewc_games_from_web

router = APIRouter()

@router.get(
    "/ewc_games",
    response_model=List[Game],
    summary="Get Esports World Cup games",
    description="""
    Returns a list of Esports World Cup 2025 games.

    - If `live=false` (default): it will try to fetch games from the local database.
    - If no games exist in the DB, it will fallback to scraping Liquipedia and update the DB.
    - If `live=true`, it will always scrape the latest data from Liquipedia and refresh the DB.
    """,
    tags=["Games"]
)
def get_ewc_games(
    live: bool = Query(False, description="Fetch from Liquipedia if True, otherwise use cached DB data")
):
    """
    Fetch games from DB or scrape from Liquipedia based on the `live` flag.
    """
    data = []

    if not live:
        data = get_games_from_db()
        if not data:
            data = fetch_ewc_games_from_web()
            if data:
                store_games_in_db(data)
    else:
        data = fetch_ewc_games_from_web()
        if data:
            store_games_in_db(data)

    return data
