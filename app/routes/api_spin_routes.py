from flask import Blueprint, jsonify, request, current_app
from app.services.slot_service import SlotService

spin_bp = Blueprint("spin_bp", __name__)

@spin_bp.route("/api/spin", methods=["POST"])
def spin():
    data = request.get_json(silent=True) or {}
    slot_count = int(data.get("slots", current_app.config["DEFAULT_SLOT_COUNT"]))
    max_slot_count = current_app.config["MAX_SLOT_COUNT"]

    result = SlotService.spin(slot_count, max_slot_count, current_app)
    if not result:
        return jsonify({"error": "No combinations configured"}), 400

    return jsonify(result)
