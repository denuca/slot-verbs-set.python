from flask import Blueprint, current_app
from app.extensions import get_redis_client

test_bp = Blueprint("test_bp", __name__, url_prefix="/api/test")

@test_bp.route("/redis")
def test_redis():
    """Test Redis connectivity"""
    try:
        redis_client = get_redis_client(current_app)
        pong = redis_client.ping()
        return f"Redis ping: {pong}"
    except RuntimeError as e:
        return str(e), 500
    except Exception as e:
        return f"Redis error: {e}", 500
