from flask import Blueprint, request, jsonify
from app.redis_repo import SlotRepository

guess_bp = Blueprint("guess_bp", __name__, url_prefix="/api")

@guess_bp.route("/guess", methods=["POST"])
def guess():
    data = request.get_json()
    combination_id = data.get("combination_id")
    user_guesses = data.get("guesses", [])

    if not combination_id or not user_guesses:
        return jsonify({"error": "Missing combination_id or guesses"}), 400

    redis_client = SlotRepository.get_redis_client()
    raw = redis_client.hget(SlotRepository.KEY, combination_id)

    if not raw:
        return jsonify({"error": "Combination not found"}), 404

    combination = json.loads(raw)
    correct_words = [s["word"] for s in combination["slots"]]

    results = [
        {"symbol": s["symbol"], "correct_word": w, "user_guess": g, "correct": g == w}
        for s, w, g in zip(combination["slots"], correct_words, user_guesses)
    ]

    return jsonify({
        "results": results,
        "difficulty": combination["difficulty"]
    })
