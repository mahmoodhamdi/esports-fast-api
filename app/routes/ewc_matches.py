# app/routes/ewc_matches_routes.py
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
from app.ewc_matches import store_matches_in_db, get_all_matches_from_db

router = APIRouter()

@router.post("/ewc_matches/update", summary="Scrape and store all EWC matches into DB")
async def update_matches():
    success, message = store_matches_in_db()
    if success:
        return JSONResponse(content={"message": message})
    raise HTTPException(status_code=500, detail=message)

@router.get("/api/ewc_matches", summary="Get all stored EWC matches with filtering and pagination")
async def list_matches(
    game: Optional[str] = Query(None, description="Filter by game name"),
    group: Optional[str] = Query(None, description="Filter by group name"),
    date: Optional[str] = Query(None, regex=r"^\d{4}-\d{2}-\d{2}$", description="Filter by date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("match_date", regex="^(match_date|match_time|game|group_name)$", description="Sort by field"),
    sort_order: Optional[str] = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    page: Optional[int] = Query(1, ge=1, description="Page number"),
    per_page: Optional[int] = Query(50, ge=1, le=100, description="Items per page")
):
    matches = get_all_matches_from_db(
        game=game,
        group=group,
        date=date,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        per_page=per_page
    )
    return {
        "message": "Matches retrieved successfully",
        "page": page,
        "per_page": per_page,
        "data": matches
    }
