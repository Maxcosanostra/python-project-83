from urllib.parse import urlparse, urlunparse
import validators


def format_date(value, format='%Y-%m-%d'):
    if value is None:
        return ""
    return value.strftime(format)


def normalize_url(input_url):
    url_parts = urlparse(input_url)
    normalized_url = urlunparse((url_parts.scheme, url_parts.netloc, '', '', '', ''))
    return normalized_url


def validate_url(input_url):
    return validators.url(input_url)
