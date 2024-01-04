import base64
from logging import getLogger
from typing import Optional

import re

import requests

logger = getLogger(__name__)


def image_url_as_base64(url: str, raise_on_error: bool = True) -> Optional[str]:
    """
    @returns base64 payload of an image url, or None on failure.
    """
    response = requests.get(url)

    if raise_on_error:
        response.raise_for_status()
    elif not response.ok:
        logger.warning(f"Failed to fetch image for {url=}; return None.")
        return None

    if (content_type := response.headers["Content-Type"]).startswith("image/"):
        return f"data:{content_type};base64,{base64.b64encode(response.content).decode('utf8')}"
    else:
        logger.warning(f"Invalid image url received; content-type is {content_type}.")
        return None


def raise_(exception: Exception):
    """
    A utility to raise exception inside a lambda.
    For testing purposes.
    """
    raise exception
