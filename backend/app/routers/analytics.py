"""Analytics router."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/team")
async def team_analytics():
    return {"message": "Team analytics - to be implemented"}
