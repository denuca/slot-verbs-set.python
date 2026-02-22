import redis
from flask import current_app


def init_redis(app):
    redis_url = app.config["REDIS_URL"]
    app.redis_client = redis.from_url(
        redis_url,
        decode_responses=True,
    )
    return app.redis_client

def get_redis_client(app=None):
    app = app or current_app._get_current_object()
    redis_client = getattr(app, "redis_client", None)
    if not redis_client:
        raise RuntimeError("Redis not initialized.")
    return redis_client