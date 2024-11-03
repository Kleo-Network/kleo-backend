# app/logging_config.py

import logging


def setup_logging():
    """
    Configure the logging settings for the application.
    """
    logging.basicConfig(
        level=logging.INFO,  # Set the logging level
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",  # Log message format
    )


# Create a logger instance that can be imported
logger = logging.getLogger(__name__)
