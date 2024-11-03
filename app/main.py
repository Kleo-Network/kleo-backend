# app/main.py
from app.mongodb import close_db_connection
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.user_v1 import router as user_router
from app.settings import settings
from app.logging_config import setup_logging, logger

# Set up logging
setup_logging()

app = FastAPI(title=settings.PROJECT_NAME)


# Add CORS middleware
origins = [
    "http://localhost:5173",  # Your local development
    "https://www.app.kleo.network",  # Your deployed app
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows only these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Include the API routers
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
