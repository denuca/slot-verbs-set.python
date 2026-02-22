import os
import hmac
import hashlib
import time
import mimetypes
import requests
from flask import current_app, abort, Response, request


class MediaService:
    """
    Handles secure streaming of private media files stored in Vercel Blob.
    """

    TOKEN_EXPIRY_SECONDS = 60  # signed URL validity

    @staticmethod
    def _generate_signature(path: str, expires: int) -> str:
        secret = current_app.config["SECRET_KEY"].encode()
        message = f"{path}:{expires}".encode()
        return hmac.new(secret, message, hashlib.sha256).hexdigest()

    @staticmethod
    def generate_signed_path(path: str) -> str:
        """
        Generates a short-lived signed path.
        """
        expires = int(time.time()) + MediaService.TOKEN_EXPIRY_SECONDS
        signature = MediaService._generate_signature(path, expires)
        return f"/api/media/{path}?expires={expires}&signature={signature}"

    @staticmethod
    def _validate_signature(path: str, expires: str, signature: str):
        if not expires or not signature:
            abort(403)

        if int(expires) < int(time.time()):
            abort(403)

        expected_sig = MediaService._generate_signature(path, int(expires))

        if not hmac.compare_digest(expected_sig, signature):
            abort(403)

    @staticmethod
    def stream_file(path: str):
        """
        Streams file securely from private Vercel Blob.
        """
        env = current_app.config.get("ENVIRONMENT", "local")

        if env == "local":
            local_root = current_app.config.get("MEDIA_STORAGE_PATH", "private_media")
            full_path = os.path.join(local_root, path)

            if not os.path.exists(full_path):
                abort(404)

            mime = mimetypes.guess_type(full_path)[0] or "application/octet-stream"

            return Response(
                open(full_path, "rb"),
                content_type=mime
            )

        # Production (Blob)
        blob_base = current_app.config.get("BLOB_BASE_URL")
        blob_token = current_app.config.get("BLOB_READ_WRITE_TOKEN")

        if not blob_base or not blob_token:
            abort(500, description="Blob not configured")

        blob_url = f"{blob_base}/{path}"

        response = requests.get(
            blob_url,
            headers={"Authorization": f"Bearer {blob_token}"},
            stream=True,
        )

        if response.status_code != 200:
            abort(404)

        return Response(
            response.iter_content(chunk_size=8192),
            content_type=response.headers.get("Content-Type"),
        )