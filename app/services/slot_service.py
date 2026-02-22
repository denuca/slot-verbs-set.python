import uuid
from flask import session
from app.redis_repository import SlotRepository
from app.utils import StringNormalizer
from app.services.media_service import MediaService

class SlotService:

    @staticmethod
    def spin(app):
        slot_key, combos = SlotRepository.get_random_slot(app)

        if not slot_key:
            return None

        symbol_string = slot_key.split(":")[1]
        symbols = symbol_string.split("-")

        image_urls = [
            MediaService.generate_signed_path_from_symbol(s, "image", app)
            for s in symbols
        ]

        audio_urls = [
            MediaService.generate_signed_path_from_symbol(s, "audio", app)
            for s in symbols
        ]

        # Reset session
        session.clear()

        return {
            "combination_id": symbol_string,
            "symbols": symbols,
            "images": image_urls,
            "audios": audio_urls,
            "total_combos": len(combos),
            "max_attempts": app.config["MAX_ATTEMPTS"]
        }

    @staticmethod
    def check_guess(slot_key: str, guesses: list[str], app=None):

        if not slot_key.startswith("slot:"):
            slot_key = f"slot:{slot_key}"

        combos = SlotRepository.get_combos(slot_key, app)

        if not combos:
            return {"error": "No combos found"}

        total_combos = len(combos)

        # Track session state
        if "found_combos" not in session:
            session["found_combos"] = []
        if "attempts_used" not in session:
            session["attempts_used"] = 0

        session["attempts_used"] += 1

        # Check if guess matches a FULL combo
        matched_combo = None
        for combo in combos:
            if guesses == combo[:len(guesses)]:
                matched_combo = combo
                break

        if matched_combo:
            combo_id = "|".join(matched_combo[:len(guesses)])
            if combo_id not in session["found_combos"]:
                session["found_combos"].append(combo_id)

        found_count = len(session["found_combos"])
        max_attempts = int(app.config["MAX_ATTEMPTS"])

        game_over = False
        win = False

        if found_count == total_combos:
            game_over = True
            win = True
        elif session["attempts_used"] >= max_attempts:
            game_over = True
            win = False

        return {
            "matched": bool(matched_combo),
            "found_count": found_count,
            "total_combos": total_combos,
            "attempts_used": session["attempts_used"],
            "max_attempts": max_attempts,
            "game_over": game_over,
            "win": win
        }