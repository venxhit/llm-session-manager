"""Authentication router."""

from fastapi import APIRouter

router = APIRouter()

# Placeholder - will be implemented later
@router.post("/register")
async def register():
    return {"message": "Registration endpoint - to be implemented"}

@router.post("/login")
async def login():
    return {"message": "Login endpoint - to be implemented"}
