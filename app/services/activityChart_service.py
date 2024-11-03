import httpx  # async HTTP client to replace `requests`
import logging
from app.settings import settings

API_KEY = settings.IMGBB_API_KEY
IMGBB_UPLOAD_IMG_ENDPOINT = f"https://api.imgbb.com/1/upload?key={API_KEY}"

logger = logging.getLogger(__name__)


async def upload_image_to_image_bb(image_data: str) -> str:
    """
    Uploads a base64 image to Imgbb and returns the image URL.

    Args:
        image_data (str): Base64 encoded image data.

    Returns:
        str: The URL of the uploaded image.
    """
    try:
        # Prepare the payload with the base64 image and the Imgbb API key
        payload = {"image": image_data, "key": API_KEY}

        # Make an async POST request to upload the image
        async with httpx.AsyncClient() as client:
            response = await client.post(IMGBB_UPLOAD_IMG_ENDPOINT, data=payload)

        # If the upload is successful, return the image URL
        if response.status_code == 200:
            response_data = response.json()

            if response_data.get("success"):
                return response_data["data"]["url_viewer"]
            else:
                logger.error("Image upload unsuccessful: %s", response_data)
                raise Exception("Image upload unsuccessful.")
        else:
            logger.error(
                "Failed to upload image. Status code: %d", response.status_code
            )
            raise Exception(
                f"Image upload failed with status code {response.status_code}"
            )

    except Exception as e:
        logger.error(f"An error occurred while uploading the image: {e}")
        raise Exception("An error occurred while uploading the image.")