import redis

_redis = None

def init_redis(app):
    """Attach Redis client to the app instance"""
    redis_url = app.config.get("REDIS_URL", "redis://localhost:6379/0")
    app.redis_client = redis.from_url(redis_url, decode_responses=True)
    return app.redis_client

def get_redis_client(app=None):
    from flask import current_app
    redis_obj = getattr(app or current_app._get_current_object(), "redis_client", None)
    if redis_obj is None:
        raise RuntimeError("Redis not initialized. Call init_redis(app) first.")
    return redis_obj
