from urllib.parse import urlparse
import validators


def validate_and_parse(url_string: str) -> dict:
    if len(url_string) == 0 or len(url_string) > 255:
        return {"error": "Некорректный URL"}
    if validators.url(url_string) is not True:
        return {"error": "Некорректный URL"}
    parsed = urlparse(url_string)
    return {"success": parsed.hostname}

