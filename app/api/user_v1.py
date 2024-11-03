# app/api/user_v1.py
import logging
from app.services.activityChart_service import upload_image_to_image_bb
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from app.services.user_service import (
    calculate_rank,
    fetch_users_referrals,
    find_by_address,
    get_top_users_by_kleo_points,
)

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


@router.get("/top-users")
async def get_top_users(
    limit: int = Query(20, description="Limit the number of top users"),
    address: str = Query(None, description="User address to fetch rank"),
):
    """
    Fetch the top users based on Kleo points and include the user's rank at the first index if the address is provided.
    """
    try:
        # Fetch the top users by Kleo points, limiting the result by the 'limit' parameter
        leaderboard = await get_top_users_by_kleo_points(limit)

        # If user_address is provided, calculate the rank and add it at the first position
        if address:
            user_rank_data = await calculate_rank(address)

            if user_rank_data:
                user_rank_entry = {
                    "address": user_rank_data["address"],
                    "kleo_points": user_rank_data["kleo_points"],
                    "rank": user_rank_data["rank"],
                }
                # Insert the user's rank at the first position in the leaderboard
                leaderboard.insert(0, user_rank_entry)
            else:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error fetching user's rank for address: {address}",
                )

        return JSONResponse(content=leaderboard, status_code=200)

    except Exception as e:
        # Return a 500 error if anything goes wrong
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching top users"
        )


@router.get("/rank/{userAddress}")
async def get_user_rank(userAddress: str):
    """
    Fetch the user's rank according to kleo_points.
    """
    try:
        rank_data = await calculate_rank(userAddress)

        # Handle error if the user is not found or if there's an issue with calculation
        if "error" in rank_data:
            raise HTTPException(status_code=404, detail=rank_data["error"])

        return rank_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching user's rank"
        )


@router.get("/referrals/{userAddress}")
async def get_user_referrals(userAddress: str):
    """
    Fetch the user's referrals based on the user's address.
    """
    try:
        referrals = await fetch_users_referrals(userAddress)

        # If an error occurs or no referrals are found
        if "error" in referrals:
            raise HTTPException(status_code=404, detail=referrals["error"])

        return referrals
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching user's referrals"
        )


@router.post("/upload_activity_chart")
async def upload_activity_chart(request: Request):
    """
    Upload an activity chart (image) and return the URL after uploading it to Imgbb.
    """
    try:
        # Retrieve the JSON data from the request
        data = await request.json()
        image_data = data.get("image")

        if not image_data:
            raise HTTPException(status_code=400, detail="No image data provided")

        # Call the function to upload the image to Imgbb
        image_url = await upload_image_to_image_bb(image_data)

        if image_url:
            return JSONResponse(content={"url": image_url}, status_code=200)
        else:
            raise HTTPException(status_code=500, detail="Image upload failed")

    except Exception as e:
        logger.error(f"An error occurred while uploading the image: {e}")
        raise HTTPException(status_code=500, detail=str(e))
