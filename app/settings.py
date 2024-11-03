# app/settings.py
import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()


class Settings:
    PROJECT_NAME: str = "KLEO Backend"
    DB_URL: str = os.getenv("DB_URL")
    DB_NAME: str = os.getenv("DB_NAME")


settings = Settings()
