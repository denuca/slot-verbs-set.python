import os
from dotenv import load_dotenv

if os.getenv("VERCEL") is None:
    load_dotenv()

class Config:
    REDIS_URL: str = os.environ.get("REDIS_URL")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev_secret")

    MAX_ATTEMPTS: int = int(os.environ.get("MAX_ATTEMPTS", 10))
    MAX_SLOT_COUNT: int = int(os.environ.get("MAX_SLOT_COUNT", 5))
    DEFAULT_SLOT_COUNT: int = int(os.environ.get("DEFAULT_SLOT_COUNT", 3))

    ENVIRONMENT: str = os.environ.get("ENVIRONMENT", "local")

    # Blob (optional in local)
    BLOB_BASE_URL: str = os.environ.get("BLOB_BASE_URL")
    BLOB_READ_WRITE_TOKEN: str = os.environ.get("BLOB_READ_WRITE_TOKEN")