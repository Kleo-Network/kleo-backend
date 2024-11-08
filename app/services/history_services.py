# app/services/user_service.py
import logging
from app.mongodb import history_collection  # Import the db object from mongodb.py

logger = logging.getLogger(__name__)


async def get_history_count(address: str) -> int:
    assert isinstance(address, str)
    
    address_pattern = re.compile(f"^{address}$", re.IGNORECASE)
    count = await history_collection.count_documents({"address": address_pattern})
    return count