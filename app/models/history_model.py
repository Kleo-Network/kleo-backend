# user.models.py
from pydantic import BaseModel
from app.services.user_service import find_by_address_complex
from app.mongodb import history_collection
from datetime import datetime
from app.models.user import User

class SaveHistoryRequest(BaseModel):
    address: str
    signup: bool
    history: list

class History:
    def __init__(
        self,
        address,
        title,
        category,
        url,
        visitTime,
        subcategory="",
        domain="",
        summary="",
        create_timestamp=int(datetime.now().timestamp()),
    ):
        assert isinstance(address, str)
        assert isinstance(create_timestamp, int)
        assert isinstance(title, str)
        assert isinstance(category, str)
        assert isinstance(subcategory, str)
        assert isinstance(url, str)
        assert isinstance(domain, str)
        assert isinstance(summary, str)
        assert isinstance(visitTime, float)

        self.document = {
            "address": address,
            "create_timestamp": create_timestamp,
            "title": title,
            "category": category,
            "subcategory": subcategory,
            "url": url,
            "domain": domain,
            "summary": summary,
            "visitTime": visitTime,
        }

    async def save(self):
        existing_user = await find_by_address_complex(self.document["address"])
        if not existing_user:
            new_user = User(address=self.document["address"])
            await new_user.save()
        # Save the history
        return await history_collection.insert_one(self.document)
