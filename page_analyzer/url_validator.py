import validators


def validate_url(url_string: str) -> tuple | None:
    errors = {}
    if len(url_string) == 0:
        return "error", "URL string can't be blank"
    if validators.url(url_string) is not True:
        return "error", "Некорректный URL"
    return None
