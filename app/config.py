import json
import os

class Config:
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

    # Load JSON config
    with open("game_config.json") as f:
        cfg = json.load(f)

    DEFAULT_SLOT_COUNT = cfg.get("default_slot_count", 3)
    MAX_SLOT_COUNT = cfg.get("max_slot_count", 5)
    MAX_ATTEMPTS = cfg.get("max_attempts", 3)

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev_key")  # for session
