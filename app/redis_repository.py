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