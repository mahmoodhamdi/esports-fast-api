import re
import os
from urllib.parse import urlparse

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_url(url):
    if not url:
        return True
    regex = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(regex.match(url))

def is_valid_thumbnail(url):
    if not url:
        return True
    image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.webp')
    parsed = urlparse(url)
    return is_valid_url(url) and (
        parsed.path.lower().endswith(image_extensions) or parsed.scheme in ('http', 'https')
    )
