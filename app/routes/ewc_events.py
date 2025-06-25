# app/routes/ewc_events.py
from fastapi import APIRouter, Query
from typing import List, Dict, Any
from app.ewc_events import fetch_ewc_events

router = APIRouter()

@router.get("/ewc_events", tags=["Events"])
def get_ewc_events(
    live: bool = Query(False, description="Fetch live data from Liquipedia if true")
) -> Dict[str, Any]:
    """
    Get Esports World Cup 2025 events data
    """
    events_data = fetch_ewc_events(live=live)

    if not events_data:
        return {
            "message": "No events data found",
            "data": []
        }

    return {
        "message": "Events data retrieved successfully",
        "data": events_data
    }
