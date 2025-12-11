# backend/cache.py
import hashlib
from datetime import datetime, timedelta

CACHE_TTL = timedelta(hours=6)
_cache: dict[str, tuple[datetime, dict]] = {}

def make_key(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def get_from_cache(text: str) -> dict | None:
    key = make_key(text)
    if key not in _cache:
        return None
    ts, value = _cache[key]
    if datetime.utcnow() - ts > CACHE_TTL:
        _cache.pop(key, None)
        return None
    return value

def store_in_cache(text: str, data: dict):
    key = make_key(text)
    _cache[key] = (datetime.utcnow(), data)