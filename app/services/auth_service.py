# auth_service.py
import os
import jwt


def get_jwt_token(wallet: str, slug: str) -> str:
    """Generate a JWT token for the user using their wallet address and slug."""
    try:
        SECRET = os.environ.get("SECRET", "default_secret")
        ALGORITHM = os.environ.get("ALGORITHM", "HS256")

        payload = {"payload": {"slug": slug, "publicAddress": wallet}}

        access_token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
        return access_token
    except Exception as e:
        print(f"An error occurred while generating JWT: {e}")
        return None
