import logging
from flask import jsonify, request
from werkzeug.exceptions import HTTPException

logger = logging.getLogger(__name__)

def register_error_handlers(app):

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        logger.warning(
            "HTTP error",
            extra={
                "path": request.path,
                "method": request.method,
                "code": e.code,
            },
        )
        return jsonify({"error": e.description}), e.code


    @app.errorhandler(Exception)
    def handle_unexpected_error(e):
        logger.exception(
            "Unhandled exception",
            extra={
                "path": request.path,
                "method": request.method,
            },
        )
        return jsonify({"error": "Internal server error"}), 500