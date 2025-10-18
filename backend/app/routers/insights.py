"""Insights router."""

from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_insights():
    return {"message": "Insights list - to be implemented"}
