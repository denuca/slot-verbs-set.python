import json
import random
from app.extensions import get_redis_client


class SlotRepository:
    INDEX_KEY = "slot:index"

    @staticmethod
    def get_all_slot_keys(app=None):
        redis_client = get_redis_client(app)
        return list(redis_client.smembers(SlotRepository.INDEX_KEY))

    @staticmethod
    def get_random_slot(app=None):
        redis_client = get_redis_client(app)
        keys = SlotRepository.get_all_slot_keys(app)

        if not keys:
            return None, None

        slot_key = random.choice(keys)
        raw = redis_client.get(slot_key)

        if not raw:
            return None, None

        return slot_key, json.loads(raw)

    @staticmethod
    def get_combos(slot_key: str, app=None):
        raw = get_redis_client(app).get(slot_key)
        if not raw:
            return []
        return json.loads(raw)

class MediaRepository:
    INDEX_KEY = "media:index"

    @staticmethod
    def get(key: str, app=None):
        raw = get_redis_client(app).get(key)
        if not raw:
            return None
        return json.loads(raw)

    @staticmethod
    def resolve_by_public_id(public_id: str, app=None):
        """
        Resolves public_id to symbol.
        Redis format:
            media:A -> ["A", "abc_replacement"]
        """
        redis_client = get_redis_client(app)

        for key in redis_client.smembers(MediaRepository.INDEX_KEY):
            raw = redis_client.get(key)
            if not raw:
                continue

            symbol, stored_public_id = json.loads(raw)

            if stored_public_id == public_id:
                return symbol

        return None