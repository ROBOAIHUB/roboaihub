from fastapi import APIRouter, Depends
from typing import List
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.user_manager import UserManager
from backend.auth import get_current_user
from backend.models import TokenData

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

user_manager = UserManager()

@router.get("/notifications")
async def get_my_notifications(current_user: TokenData = Depends(get_current_user)):
    """
    Get notifications for the logged-in user.
    """
    notifs = user_manager.get_notifications(current_user.username)
    # Reverse to show newest first
    return notifs[::-1]
