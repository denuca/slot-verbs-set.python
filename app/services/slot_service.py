import random
import secrets
from app.redis_repo import SlotRepository
from app.extensions import get_redis_client  # ✅ import here

class SlotService:

    @staticmethod
    def spin(slot_count: int, max_slot_count: int, app=None):
        """
        Generate a random symbol combination.
        Returns a dict with combination_id, symbols, session_id, max_attempts
        """
        if slot_count < 1 or slot_count > max_slot_count:
            raise ValueError(f"slot_count must be between 1 and {max_slot_count}")

        # ✅ use get_redis_client(app) directly
        redis_client = get_redis_client(app)
        all_combos = redis_client.hkeys(SlotRepository.KEY)
        if not all_combos:
            return None

        # Filter combinations by requested slot count
        valid_combos = [c for c in all_combos if len(c.split(",")) == slot_count]
        if not valid_combos:
            return None

        # Pick a random combination
        combo_str = random.choice(valid_combos)
        symbols = combo_str.split(",")

        return {
            "combination_id": combo_str,
            "symbols": symbols,
            "session_id": secrets.token_urlsafe(16),
            "max_attempts": 5
        }

    @staticmethod
    def check_guess(symbol_combo: list[str], user_guess: list[str], app=None):
        """
        Check user's guess per slot against all valid sets.
        Each word is validated independently.
        """

        valid_sets = SlotRepository.get_valid_sets(symbol_combo, app)
        if not valid_sets:
            return []

        # Extract all valid value lists
        valid_value_sets = [vs["values"] for vs in valid_sets]

        results = []

        for idx, symbol in enumerate(symbol_combo):
            guessed_word = user_guess[idx]

            # Check if guessed word matches ANY valid set at this position
            correct = any(
                guessed_word == valid_values[idx]
                for valid_values in valid_value_sets
            )

            results.append({
                "symbol": symbol,
                "user_guess": guessed_word,
                "correct": correct
            })

        return results
