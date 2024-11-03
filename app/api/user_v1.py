# app/api/user_v1.py
import logging
from fastapi import APIRouter, HTTPException
from app.services.user_service import find_by_address

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/get-user/{userAddress}")
async def get_user(userAddress: str):
    """
    Fetch user data from MongoDB based on the user's address.
    """
    user_data = await find_by_address(userAddress)

    # If user data is not found, raise a 404 error
    if user_data is None:
        raise HTTPException(status_code=404, detail="User not found")

    # Return the user data directly as JSON
    return user_data
