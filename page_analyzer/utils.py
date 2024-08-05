import validators
from urllib.parse import urlparse


def normalize_url(input_url):
    parsed_url = urlparse(input_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def validate_url(input_url):
    if not input_url:
        return 'URL обязателен для заполнения'
    if len(input_url) > 255:
        return 'Введенный URL превышает длину в 255 символов'
    if not validators.url(input_url):
        return 'Некорректный URL'
    return None
