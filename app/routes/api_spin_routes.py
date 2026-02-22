from flask import Blueprint, jsonify, current_app
from app.services.slot_service import SlotService

spin_bp = Blueprint("spin_bp", __name__)


@spin_bp.route("/api/spin", methods=["POST"])
def spin():
    result = SlotService.spin(current_app)
    print(f"result: {result}")

    if not result:
        return jsonify({"error": "No slot data in Redis"}), 400

    return jsonify(result)