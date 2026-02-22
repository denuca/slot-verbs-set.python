import os
from dotenv import load_dotenv

if os.getenv("VERCEL") is None:
    load_dotenv()

def get_environment():
    """
    Detects current environment:
    - 'local' if ENVIRONMENT=local or no VERCEL vars
    - 'vercel' if running on Vercel Free Tier
    """
    env = os.environ.get("ENVIRONMENT")
    if env:
        return env.lower()
    if os.environ.get("VERCEL") == "1":
        return "vercel"
    return "local"

class Config:
    ENVIRONMENT: str = get_environment()
    REDIS_URL: str = os.environ.get("REDIS_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_secret")

    MAX_ATTEMPTS: int = int(os.environ.get("MAX_ATTEMPTS", 10))
    MAX_SLOT_COUNT: int = int(os.environ.get("MAX_SLOT_COUNT", 5))
    DEFAULT_SLOT_COUNT: int = int(os.environ.get("DEFAULT_SLOT_COUNT", 3))

    # Blob (optional in local)
    BLOB_BASE_URL: str = os.environ.get("BLOB_BASE_URL")
    BLOB_READ_WRITE_TOKEN: str = os.environ.get("BLOB_READ_WRITE_TOKEN")

    MEDIA_STORAGE = {
        "image": {
            "folder": "images",
            "extension": "png"
        },
        "audio": {
            "folder": "audios",
            "extension": "mp3"
        }
    }