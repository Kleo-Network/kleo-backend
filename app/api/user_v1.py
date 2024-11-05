# app/api/user_v1.py
import logging
import random
import httpx
from app.const.historyConst import ABI, POLYGON_RPC
from app.services.activityChart_service import (
    get_top_activities,
    upload_image_to_image_bb,
)
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from app.services.auth_service import get_jwt_token
from app.services.user_service import (
    calculate_rank,
    fetch_users_referrals,
    find_by_address,
    find_by_address_complex,
    find_referral_in_history,
    get_activity_json,
    get_history_count,
    get_top_users_by_kleo_points,
    update_referee_and_bonus,
)
from app.models.user_models import CreateUserRequest, SaveHistoryRequest, User

CELERY_API_BASE_URL = "https://api.kleo.network/api/v1/core/tasks/tasks"

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


@router.get("/get-user-graph/{userAddress}")
async def get_user_graph(userAddress: str):
    """Fetch user graph data based on the user's activity."""
    try:
        if not userAddress:
            raise HTTPException(status_code=400, detail="Address is required")

        # Directly get the activity json
        activity_json = await get_activity_json(userAddress)
        if not activity_json:
            return {"error": "No activity data available"}, 404

        # Get top activities from the activity_json
        top_activities = await get_top_activities(activity_json)

        return {"data": top_activities}

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise HTTPException(
            status_code=500, detail="An error occurred while fetching user graph data."
        )


@router.post("/create-user")
async def create_user(request: CreateUserRequest):
    """Create a new user or retrieve existing user data."""
    wallet_address = request.address

    if not wallet_address:
        raise HTTPException(status_code=400, detail="Address is required")

    user = await find_by_address(wallet_address)  # Call async function
    if user:
        try:
            token = get_jwt_token(wallet_address, wallet_address)
        except Exception as e:
            raise HTTPException(status_code=500, detail="Failed to generate token")

        user_data = {"password": user["slug"], "token": token}
        return user_data

    random_code = str(random.randint(100, 9999999))

    user = User(address=wallet_address, slug=random_code)
    response = await user.save(signup=True)  # Call async save method

    try:
        token = get_jwt_token(wallet_address, wallet_address)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate token")

    user_data = {
        "password": response["slug"],
        "token": token,
    }

    return user_data


@router.post("/save-history")
async def save_history(request: SaveHistoryRequest):
    try:
        user_address = request.address.lower()
        signup = request.signup
        history = request.history  # Treat history as a list of dictionaries
        return_abi_contract = False

        # Fetch the user by address
        user = await find_by_address_complex(user_address)

        try:
            if signup:
                referee_address = await find_referral_in_history(history)
                if referee_address:
                    await update_referee_and_bonus(user_address, referee_address)

                # Replace CELERY task with API call (classify-batch-activity)
                batch_activity_url = f"{CELERY_API_BASE_URL}/classify-batch-activity"
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        batch_activity_url,
                        json={"address": user_address, "history": history},
                    )

                logger.info(f"Batch Activity API response: {response.json()}")

                # Check if the task was accepted (202 status)
                if response.status_code == 202:
                    return {"data": "Signup successful!"}
                else:
                    raise HTTPException(
                        status_code=response.status_code, detail=response.text
                    )

            else:
                # Check if the user has more than 50 history records
                if await get_history_count(user_address) > 50:
                    return_abi_contract = True

                task_responses = []  # To collect all task responses

                # Iterate over each item in the history and trigger API calls
                for item in history:
                    if item.get(
                        "content"
                    ):  # Check if 'content' field exists in the dictionary
                        single_activity_url = (
                            f"{CELERY_API_BASE_URL}/classify-single-activity"
                        )

                        async with httpx.AsyncClient() as client:
                            response = await client.post(
                                single_activity_url,
                                json={
                                    "address": user_address,
                                    "activity": item,
                                },  # Send plain dicts
                            )

                        # logger.info(f"Single Activity API response: {response.json()}")

                        # Handle 202 status code as success
                        if response.status_code == 202:
                            task_responses.append(response.json())
                        else:
                            raise HTTPException(
                                status_code=response.status_code, detail=response.text
                            )

                # Log all task responses for activities
                logger.info(f"All task responses: {task_responses}")

                if return_abi_contract:
                    user = await find_by_address_complex(user_address)
                    previous_hash = user.get("previous_hash", "first_hash")
                    chain_data_list = [
                        {
                            "name": "polygon",
                            "rpc": POLYGON_RPC,
                            "contractData": {
                                "address": "0xD133A1aE09EAA45c51Daa898031c0037485347B0",
                                "abi": ABI,
                                "functionName": "safeMint",
                                "functionParams": [
                                    user_address,
                                    previous_hash,
                                ],
                            },
                        }
                    ]

                    response_data = {
                        "chains": chain_data_list,
                        "password": user.get("slug"),
                    }
                    return {"data": response_data}

                # Return all task responses if successful
                return {
                    "status": "success",
                    "tasks": task_responses,
                    "message": "History saved successfully",
                }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
