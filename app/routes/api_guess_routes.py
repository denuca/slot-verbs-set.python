from flask import Blueprint, jsonify, request, current_app
from app.services.slot_service import SlotService
from app.utils import StringNormalizer

guess_bp = Blueprint("guess_bp", __name__)


@guess_bp.route("/api/guess", methods=["POST"])
def guess():
    data = request.get_json(silent=True) or {}

    slot_key = data.get("combination_id")
    guesses = StringNormalizer.normalize_list(data.get("guesses"))
    print(f"guesses: {guesses}")

    if not slot_key or not guesses:
        return jsonify({"error": "Missing data"}), 400

    result = SlotService.check_guess(slot_key, guesses, current_app)

    return jsonify(result)