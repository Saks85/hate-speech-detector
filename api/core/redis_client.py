import redis
import hashlib
import json
from hate_speech.config import settings

if settings.REDIS_URL:
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
else:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        ssl=settings.REDIS_SSL,
        decode_responses=True,
    )

def text_hash(text: str):
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()

def get_override(text: str):
    key = f"hate_override:{text_hash(text)}"
    try:
        data = redis_client.get(key)
        if data:
            return json.loads(data)
    except redis.RedisError:
        # Gracefully degrade when Redis is unavailable.
        return None
    return None

def set_override(text: str, label: str, moderator="system"):
    key = f"hate_override:{text_hash(text)}"
    value = json.dumps({
        "label": label,
        "source": "human_override",
        "moderator": moderator
    })
    try:
        redis_client.set(key, value)
    except redis.RedisError:
        # Ignore cache-store failures; DB feedback still persists.
        pass

def clear_prediction_cache():
    """
    Clears all cached prediction results.
    Safe to call after model reload.
    """
    # OPTION 1: Clear everything (simple & safe for now)
    try:
        redis_client.flushdb()
    except redis.RedisError:
        pass