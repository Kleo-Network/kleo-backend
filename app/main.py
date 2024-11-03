# app/main.py
from app.mongodb import close_db_connection
from fastapi import FastAPI
from app.api.health import router as health_router
from app.api.user_v1 import router as user_router
from app.settings import settings
from app.logging_config import setup_logging, logger

# Set up logging
setup_logging()

app = FastAPI(title=settings.PROJECT_NAME)

# Include the API router
app.include_router(health_router, prefix="/api")
app.include_router(user_router, prefix="/api/v1/user")


@app.get("/")
async def root():
    return {"message": "Welcome to the FastAPI application!"}


# Optional: Log startup events
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up the FastAPI application.")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down the FastAPI application.")
    await close_db_connection()
