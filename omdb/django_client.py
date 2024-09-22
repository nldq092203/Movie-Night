from django.conf import settings
from omdb.client import OmdbClient
import logging

logger = logging.getLogger(__name__)

def get_client_from_settings():
    """Create an instance of an OmdbClient using the OMDB_KEY from the Django settings."""
    logger.warning ("Omdb object created")
    return OmdbClient(settings.OMDB_KEY)