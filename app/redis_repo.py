import json
from app.extensions import get_redis_client

class SlotRepository:
    KEY = "slot:combinations"

    @staticmethod
    def get_valid_sets(symbol_combo: list[str], app=None) -> list[dict]:
        """
        Returns a list of valid sets with difficulty for a given symbol combo.
        Each set is a dict: {"values": [...], "difficulty": "easy|difficult"}
        """
        redis_client = get_redis_client(app)
        combo_str = ",".join(symbol_combo)
        raw = redis_client.hget(SlotRepository.KEY, combo_str)
        if not raw:
            return []
        return json.loads(raw)

    @staticmethod
    def mark_found(symbol_combo: list[str], values: list[str], app=None):
        """
        Optionally track which sets were already found (can store in Redis or session).
        """
        pass
