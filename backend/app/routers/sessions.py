"""Sessions router."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_sessions():
    return {"message": "Sessions list - to be implemented"}
