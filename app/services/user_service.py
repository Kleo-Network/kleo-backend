# app/services/user_service.py
import logging
from app.mongodb import db  # Import the db object from mongodb.py

logger = logging.getLogger(__name__)


async def find_by_address(address: str) -> dict:
    """
    Fetch user data from MongoDB based on the user's address.
    """
    user_data = await db.users.find_one({"address": address})

    if user_data:
        user_data["_id"] = str(user_data["_id"])
        return user_data
    return None
