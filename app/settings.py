# app/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class Settings:
    PROJECT_NAME: str = "KLEO Backend"
    DB_URL: str = os.getenv("DB_URL")
    DB_NAME: str = os.getenv("DB_NAME")
    IMGBB_API_KEY: str = os.getenv("IMGBB_API_KEY")
    POLYGON_RPC: str = os.getenv("POLYGON_RPC")
    CELERY_BROKER_URL: str = os.getenv("CELERY_BROKER_URL")
    CELERY_RESULT_BACKEND: str = os.getenv("CELERY_RESULT_BACKEND")


settings = Settings()
