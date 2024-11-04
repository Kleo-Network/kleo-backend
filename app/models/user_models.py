# user.models.py
from typing import List, Optional
from pydantic import BaseModel
from app.services.user_service import find_by_address_complex
from app.mongodb import user_collection


class CreateUserRequest(BaseModel):
    address: str


class SaveHistoryRequest(BaseModel):
    address: str
    signup: bool
    history: list


class HistoryItem(BaseModel):
    content: Optional[str] = None


class SaveHistoryRequest(BaseModel):
    address: str
    signup: bool = False
    history: List[HistoryItem] = []


class User:
    def __init__(
        self,
        address: str,
        slug: str,
        stage: int = 1,
        name: str = "",
        pfp: str = "",
        previous_hash: str = "",
        verified: bool = False,
        last_cards_marked: int = 0,
        about: str = "",
        content_tags: list = None,
        last_attested: int = 0,
        identity_tags: list = None,
        badges: list = None,
        kleo_points: int = 0,
        settings: dict = None,
        first_time_user: bool = True,
        total_data_quantity: int = 0,
        activity_json: dict = None,
        milestones: dict = None,
        referrals: list = None,
        referee: str = None,
        pii_removed_count: int = 0,
    ):
        if content_tags is None:
            content_tags = []
        if identity_tags is None:
            identity_tags = []
        if badges is None:
            badges = []
        if settings is None:
            settings = {}
        if activity_json is None:
            activity_json = {}
        if milestones is None:
            milestones = {
                "tweet_activity_graph": False,
                "data_owned": 0,
                "referred_count": 0,
                "followed_on_twitter": False,
            }
        if referrals is None:
            referrals = []

        # Type assertions for validation
        assert isinstance(address, str)
        assert isinstance(slug, str)
        assert isinstance(stage, int)
        assert isinstance(name, str)
        assert isinstance(verified, bool)
        assert isinstance(last_cards_marked, int)
        assert isinstance(about, str)
        assert isinstance(pfp, str)
        assert isinstance(content_tags, list)
        assert isinstance(last_attested, int)
        assert isinstance(identity_tags, list)
        assert isinstance(badges, list)
        assert isinstance(kleo_points, int)
        assert isinstance(settings, dict)
        assert isinstance(first_time_user, bool)
        assert isinstance(total_data_quantity, int)
        assert isinstance(milestones, dict)
        assert isinstance(referrals, list)
        assert referee is None or isinstance(referee, str)
        assert isinstance(pii_removed_count, int)

        self.document = {
            "address": address,
            "slug": slug,
            "name": name,
            "stage": stage,
            "verified": verified,
            "last_cards_marked": last_cards_marked,
            "about": about,
            "pfp": pfp,
            "content_tags": content_tags,
            "last_attested": last_attested,
            "identity_tags": identity_tags,
            "badges": badges,
            "kleo_points": kleo_points,
            "settings": settings,
            "first_time_user": first_time_user,
            "total_data_quantity": total_data_quantity,
            "milestones": milestones,
            "referrals": referrals,
            "referee": referee,
            "pii_removed_count": pii_removed_count,
        }

    async def save(self, signup: bool = False):
        existing_user_address = await find_by_address_complex(
            self.document["address"]
        )  # Ensure this function is async
        if existing_user_address:
            return existing_user_address
        else:
            await user_collection.insert_one(
                self.document
            )  # Make sure this is an async call
        return self.document
