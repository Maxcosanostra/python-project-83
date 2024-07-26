from urllib.parse import urlparse
import validators


def normalize_url(input_url):
    parsed_url = urlparse(input_url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"


def validate_url(input_url):
    return validators.url(input_url)


def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)
