from fastapi import APIRouter, Query
from typing import Dict, Any
from app.ewc_info import get_ewc_information

router = APIRouter()

@router.get("/ewc_info", response_model=Dict[str, Any], tags=["EWC Info"])
def get_ewc_info(
    live: bool = Query(False, description="Fetch fresh data from Liquipedia if true")
):
    """
    Get Esports World Cup 2025 information
    """
    info_data = get_ewc_information(live=live)

    if not info_data:
        return {
            "message": "No information found",
            "data": {}
        }

    return {
        "message": "EWC information retrieved successfully",
        "data": info_data
    }
