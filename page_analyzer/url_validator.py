import validators


def validate_url(url_string: str) -> str | None:
    if len(url_string) == 0:
        return "URL string can't be blank"
    if validators.url(url_string) is not True:
        return "Некорректный URL"
    return None
