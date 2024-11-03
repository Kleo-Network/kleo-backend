# app/mongodb.py
import motor.motor_asyncio  # type: ignore
from app.settings import settings

# Create a MongoDB client
client = motor.motor_asyncio.AsyncIOMotorClient(settings.DB_URL)
db = client[settings.DB_NAME]  # Access the database using the name from settings


async def close_db_connection():
    """
    Close the MongoDB client connection.
    """
    if client is not None:
        await client.close()
    else:
        print("MongoDB client is not initialized.")
