"""Teams router."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_teams():
    return {"message": "Teams list - to be implemented"}
