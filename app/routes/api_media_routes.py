from flask import Blueprint
from app.services.media_service import MediaService

media_bp = Blueprint("media_bp", __name__)

@media_bp.route("/api/media/<path:public_id>")
def serve_media(public_id):
    return MediaService.stream_file(public_id)