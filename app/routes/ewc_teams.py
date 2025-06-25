# app/routes/ewc_teams.py
from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.ewc_teams import fetch_ewc_teams

router = APIRouter()

@router.get("/ewc_teams", tags=["Teams"])
def get_ewc_teams(
    live: bool = Query(False, description="Fetch live data from Liquipedia if true")
) -> Dict[str, Any]:
    """
    Get Esports World Cup 2025 teams data
    """
    teams_data = fetch_ewc_teams(live=live)

    if not teams_data:
        return {
            "message": "No teams data found",
            "data": []
        }

    return {
        "message": "Teams data retrieved successfully",
        "data": teams_data
    }
