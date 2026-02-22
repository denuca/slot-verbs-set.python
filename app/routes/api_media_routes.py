from flask import Blueprint
from app.services.media_service import MediaService

media_bp = Blueprint("media_bp", __name__)

@media_bp.route("/api/media/<path:path>")
def serve_media(path):
    return MediaService.stream_file(path)