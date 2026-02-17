from flask import Blueprint, jsonify, request, current_app
from app.services.slot_service import SlotService

guess_bp = Blueprint("guess_bp", __name__)

@guess_bp.route("/api/guess", methods=["POST"])
def guess():
    data = request.get_json(silent=True) or {}
    combination_id = data.get("combination_id")
    user_guess = data.get("guesses")

    if not combination_id or not user_guess:
        return jsonify({"error": "Missing combination_id or guesses"}), 400

    symbols = combination_id.split(",")
    results = SlotService.check_guess(symbols, user_guess, current_app)
    return jsonify({"results": results})
