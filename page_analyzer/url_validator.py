from urllib.parse import urlparse

import validators


def validate_url(url_string: str) -> dict:
    invalid_length = len(url_string) == 0 or len(url_string) > 255
    invalid_format = validators.url(url_string) is not True
    if invalid_format or invalid_length:
        return {
            "status": "error"
        }
    return {
        "status": "success"
    }
