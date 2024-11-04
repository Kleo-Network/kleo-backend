# app/services/user_service.py
from datetime import datetime, timezone
import logging
from urllib.parse import parse_qs, urlparse
from app.mongodb import db  # Import the db object from mongodb.py

logger = logging.getLogger(__name__)


# Get the User data based on the user's address.
async def find_by_address(address: str) -> dict:
    """
    Fetch user data from MongoDB based on the user's address.
    """
    try:
        # Use find_one to fetch the user data based on the address
        user_data = await db.users.find_one({"address": address})

        if user_data:
            user_data["_id"] = str(user_data["_id"])
            return user_data

    except Exception as e:
        # Log the exception if needed
        print(f"An error occurred while fetching user by address: {e}")
        return None  # Return None on error


# Get the User data based on the user's address with complex pipeline.
async def find_by_address_complex(address: str) -> dict:
    """
    Fetch user data from MongoDB based on the user's address using aggregation.
    """
    try:
        pipeline = [
            {"$match": {"$expr": {"$eq": [{"$toLower": "$address"}, address.lower()]}}},
            {"$project": {"_id": 0}},  # Exclude the _id field
        ]

        # Use aggregate with motor to fetch the data
        user_cursor = db.users.aggregate(pipeline)

        # Convert the cursor to a list to fetch the first document
        user_of_db = await user_cursor.to_list(length=1)

        if user_of_db:
            return user_of_db[0]  # Return the first user document
        return None  # No user found

    except Exception as e:
        # Log the exception if needed
        print(f"An error occurred while fetching user by address: {e}")
        return None  # Return None on error


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


async def find_referral_in_history(history):
    """
    Finds the referrer address in the user's history if available.
    Looks for visits to the Chrome Web Store with a 'refAddress' parameter.
    Example URL:
    https://chromewebstore.google.com/detail/kleo-network/jimpblheogbjfgajkccdoehjfadmimoo?refAddress=XYZ
    """
    for item in history:
        url = item.get("url")
        if url and "chromewebstore.google.com/detail/kleo-network" in url:
            # Parse the query parameters to find 'refAddress'
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            ref_address = query_params.get("refAddress")
            if ref_address:
                return ref_address[0]  # Return the first 'refAddress' found

    return None


async def update_referee_and_bonus(user_address: str, referee_address: str):
    """
    Updates the user's referee information and assigns the referral bonus.
    """
    try:
        # Get the current timestamp in milliseconds for the joining date
        current_timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

        referral_bonus = 100

        # Add the referee to the user's record
        await db.users.update_one(
            {"address": user_address}, {"$set": {"referee": referee_address}}
        )

        # Update the kleo_points and referred_count for the referee, and push the referred user to the referrals list
        await db.users.update_one(
            {"address": referee_address},
            {
                "$inc": {
                    "kleo_points": referral_bonus,
                    "milestones.referred_count": 1,  # Increment referred_count by 1
                },
                "$push": {
                    "referrals": {
                        "address": user_address,
                        "joining_date": {"$numberLong": str(current_timestamp)},
                    }
                },
            },
        )

        # Update kleo_points for the referred user
        await db.users.update_one(
            {"address": user_address}, {"$inc": {"kleo_points": referral_bonus}}
        )
    except Exception as e:
        # Log the exception for debugging
        print(f"An error occurred while updating referral: {e}")


async def get_history_count(address: str) -> int:
    """
    Asynchronously fetch the count of history documents for a given address.
    """
    count = await db.history.count_documents({"address": address})
    return count
