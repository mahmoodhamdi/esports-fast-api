from fastapi import APIRouter, Query
from typing import List, Optional, Dict, Any
from app.prizes import get_prize_distribution

router = APIRouter()

@router.get("/ewc_prize_distribution")
def get_ewc_prize_distribution(
    live: bool = Query(False, description="Fetch fresh data from Liquipedia if true"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    per_page: int = Query(10, ge=1, le=100, description="Number of items per page"),
    filter: Optional[str] = Query(None, description="Filter by place or prize")
) -> Dict[str, Any]:
    """
    Get Esports World Cup 2025 prize distribution
    """
    prize_data = get_prize_distribution(live=live)
    
    if not prize_data:
        return {
            "message": "No prize distribution data found",
            "data": [],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": 0,
                "pages": 0
            }
        }

    # Apply filtering
    if filter:
        prize_data = [
            item for item in prize_data
            if filter.lower() in item['place'].lower() or
               filter.lower() in item['prize'].lower()
        ]

    # Apply pagination
    total = len(prize_data)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = prize_data[start:end]

    return {
        "message": "Prize distribution data retrieved successfully",
        "data": paginated_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
