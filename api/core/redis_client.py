import redis
import hashlib
import json

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

def text_hash(text: str):
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()

def get_override(text: str):
    key = f"hate_override:{text_hash(text)}"
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_override(text: str, label: str, moderator="system"):
    key = f"hate_override:{text_hash(text)}"
    value = json.dumps({
        "label": label,
        "source": "human_override",
        "moderator": moderator
    })
    redis_client.set(key, value)