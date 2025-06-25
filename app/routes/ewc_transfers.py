from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.ewc_transfers import store_transfers_in_db, get_transfers_from_db

router = APIRouter()

@router.post("/ewc_transfers/update")
def update_transfers(game: str = Query(..., description="Game name (e.g., 'valorant')")):
    success, message = store_transfers_in_db(game.lower())
    if success:
        return {"message": message}
    raise HTTPException(status_code=500, detail=message)

@router.get("/ewc_transfers")
def list_transfers(
    game: Optional[str] = Query(None, description="Game name to filter"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    sort_by: str = Query("date", regex="^(date|player_name|game|old_team_name|new_team_name)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    result = get_transfers_from_db(
        game_name=game.lower() if game else None,
        page=page,
        per_page=per_page,
        sort_by=sort_by,
        sort_order=sort_order
    )
    return {
        "message": "Transfers retrieved successfully",
        "total": result["total"],
        "page": result["page"],
        "per_page": result["per_page"],
        "data": result["data"]
    }
