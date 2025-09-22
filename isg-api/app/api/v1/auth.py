from fastapi import APIRouter
from app.auth import create_demo_token, UserRole

router = APIRouter()

@router.get("/demo-token/{role}")
async def get_demo_token(role: UserRole):
    """
    Generate a demo token for testing purposes.
    In production, this would be replaced with proper authentication.
    """
    token = create_demo_token(f"demo_{role.lower()}", role)
    return {"access_token": token, "token_type": "bearer", "role": role}