#from flask import Blueprint, jsonify, request, render_template, current_app
#from ..services.slot_service import SlotService
#
#slot_bp = Blueprint("slot_bp", __name__)
#
#@slot_bp.route("/")
#def home():
#    return render_template("index.html")
#
#
#@slot_bp.route("/api/spin", methods=["POST"])
#def spin():
#    data = request.get_json(silent=True) or {}
#    slot_count = int(
#        data.get("slots", current_app.config["DEFAULT_SLOT_COUNT"])
#    )
#
#    try:
#        result = SlotService.spin(
#            slot_count,
#            current_app.config["MAX_SLOT_COUNT"],
#        )
#    except ValueError as e:
#        return jsonify({"error": str(e)}), 400
#
#    if not result:
#        return jsonify({"error": "No combinations configured"}), 400
#
#    return jsonify(result)
#
#@slot_bp.route("/api/test_redis")
#def test_redis():
#    from app.extensions import redis_client
#    if redis_client is None:
#        return "Redis not initialized", 500
#    try:
#        pong = redis_client.ping()
#        return f"Redis ping: {pong}"
#    except Exception as e:
#        return f"Redis error: {e}", 500
#