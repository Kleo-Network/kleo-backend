# app/services/user_service.py
import logging
from app.mongodb import db  # Import the db object from mongodb.py

logger = logging.getLogger(__name__)


# Get the User data based on the user's address.
async def find_by_address(address: str) -> dict:
    """
    Fetch user data from MongoDB based on the user's address.
    """
    user_data = await db.users.find_one({"address": address})

    if user_data:
        user_data["_id"] = str(user_data["_id"])
        return user_data
    return None


# Get top N users based on KleoPoints. Leaderboard.
async def get_top_users_by_kleo_points(limit=10):
    try:
        # Fetch users sorted by Kleo points in descending order, limit the result to `limit`
        cursor = (
            db.users.find(
                {},  # No filter, fetch all users
                {
                    "_id": 0,  # Exclude `_id`
                    "address": 1,  # Include `address`
                    "kleo_points": 1,  # Include `kleo_points`
                },
            )
            .sort("kleo_points", -1)  # Sort by `kleo_points` in descending order (-1)
            .limit(limit)
        )  # Limit the number of results to `limit`

        # Convert cursor to a list of users asynchronously
        users = await cursor.to_list(length=limit)

        # Format the result into a leaderboard
        leaderboard = [
            {
                "rank": index,  # Rank starts from 1
                "address": user["address"],  # Include user's address
                "kleo_points": user.get("kleo_points", 0),  # Include kleo_points
            }
            for index, user in enumerate(users, start=1)
        ]

        return leaderboard
    except Exception as e:
        logger.error(f"An error occurred while fetching top users: {e}")
        return []


# Calculate the user's rank based on their Kleo points compared to other users.
async def calculate_rank(address: str):
    try:
        # First, get the user's Kleo points by address
        user = await db.users.find_one(
            {"address": address}, {"kleo_points": 1, "_id": 0}
        )

        if not user:
            return {"error": "User not found"}, 404

        user_kleo_points = user.get("kleo_points", 0)

        # Count how many users have more Kleo points
        higher_ranked_users = await db.users.count_documents(
            {"kleo_points": {"$gt": user_kleo_points}}
        )

        # The rank is the number of users with more points, plus one
        rank = higher_ranked_users + 1

        # Get total number of users
        total_users = await db.users.count_documents({})

        return {
            "address": address,
            "kleo_points": user_kleo_points,
            "rank": rank,
            "total_users": total_users,
        }

    except Exception as e:
        logger.error(
            f"An error occurred while calculating rank for address {address}: {e}"
        )
        return {"error": "An error occurred while calculating rank"}, 500


async def fetch_users_referrals(address: str) -> list:
    """
    Fetch the user's referrals from MongoDB and include their kleo points.
    """
    try:
        # Fetch the user's data based on the address
        user = await db.users.find_one({"address": address})

        if not user:
            return {"error": "User not found"}, 404

        # Get the referrals list from the user's data
        referrals = user.get("referrals", [])
        if not referrals:
            return []

        # Initialize a list to store referral details
        referral_details = []

        # Iterate through each referral and get their kleo_points
        for referral in referrals:
            referred_user = await db.users.find_one(
                {"address": referral["address"]}, {"kleo_points": 1, "_id": 0}
            )

            # Extract kleo_points if user is found, otherwise default to 0
            kleo_points = referred_user.get("kleo_points", 0) if referred_user else 0

            # Append the referral data along with kleo_points
            referral_details.append(
                {
                    "address": referral["address"],
                    "joining_date": referral["joining_date"],
                    "kleo_points": kleo_points,
                }
            )

        return referral_details

    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return {"error": "An error occurred while fetching referrals."}, 500


async def get_activity_json(address):
    """Fetch the user's activity JSON from the database."""
    try:
        user = await db.users.find_one(
            {"address": address},
            {"_id": 0, "activity_json": 1},  # Exclude _id, include only activity_json
        )

        if user:
            return user.get("activity_json", "")  # Return activity_json if it exists
        else:
            return {}  # Return empty dict if user not found

    except Exception as e:
        print(f"An error occurred while retrieving activity json: {e}")
        return None
