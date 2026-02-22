import os
import hmac
import hashlib
import time
import mimetypes
import requests
from flask import current_app, abort, Response, request
from app.redis_repository import MediaRepository
from app.utils import StringNormalizer

class MediaService:

    TOKEN_EXPIRY_SECONDS = 5

    # -----------------------
    # Signature
    # -----------------------

    @staticmethod
    def _generate_signature(public_id: str, expires: int) -> str:
        secret = current_app.config["SECRET_KEY"].encode()
        message = f"{public_id}:{expires}".encode()
        return hmac.new(secret, message, hashlib.sha256).hexdigest()

    @staticmethod
    def _validate_signature(public_id: str, expires: str, signature: str):
        if not expires or not signature:
            abort(403)

        if int(expires) < int(time.time()):
            abort(403)

        expected_sig = MediaService._generate_signature(public_id, int(expires))

        if not hmac.compare_digest(expected_sig, signature):
            abort(403)

    # -----------------------
    # URL Generation
    # -----------------------

    @staticmethod
    def generate_signed_path_from_symbol(symbol: str, media_type: str, app):

        media_entry = MediaRepository.get(f"media:{symbol}", app)

        if not media_entry:
            print(f"[MEDIA] No Redis entry for symbol: {symbol}")
            return ""

        _, public_id = media_entry

        expires = int(time.time()) + MediaService.TOKEN_EXPIRY_SECONDS
        signature = MediaService._generate_signature(public_id, expires)

        # IMPORTANT: include media_type in query
        return f"/api/media/{public_id}?type={media_type}&expires={expires}&signature={signature}"

    # -----------------------
    # Streaming
    # -----------------------

    @staticmethod
    def stream_file(public_id: str):

        media_type = request.args.get("type")
        expires = request.args.get("expires")
        signature = request.args.get("signature")

        if not media_type:
            abort(400, description="Missing media type")

        MediaService._validate_signature(public_id, expires, signature)

        symbol = StringNormalizer.normalize(MediaRepository.resolve_by_public_id(public_id, current_app))

        if not symbol:
            print("[MEDIA] Public ID not found in Redis")
            abort(404)

        media_config = current_app.config["MEDIA_STORAGE"].get(media_type)

        if not media_config:
            abort(400, description="Invalid media type")

        folder = media_config["folder"]
        extension = media_config["extension"]

        blob_path = f"{folder}/{symbol}.{extension}"

        env = current_app.config.get("ENVIRONMENT", "local")

        # -----------------------
        # LOCAL
        # -----------------------
        if env == "local":
            local_root = current_app.config.get("MEDIA_STORAGE_PATH", "private_media")
            full_path = os.path.join(local_root, blob_path)

            if not os.path.exists(full_path):
                print("[MEDIA] Local file not found")
                abort(404)

            mime = mimetypes.guess_type(full_path)[0] or "application/octet-stream"

            return Response(open(full_path, "rb"), content_type=mime)

        # -----------------------
        # BLOB
        # -----------------------
        blob_base = current_app.config.get("BLOB_BASE_URL")
        blob_token = current_app.config.get("BLOB_READ_WRITE_TOKEN")

        if not blob_base or not blob_token:
            abort(500, description="Blob not configured")

        blob_url = f"{blob_base}/{blob_path}"

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