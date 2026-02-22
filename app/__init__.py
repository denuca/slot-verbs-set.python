import os
from flask import Flask
from app.extensions import init_redis
from app.errors import register_error_handlers
from app.config import Config

def create_app():
    """
    Factory to create a Flask app.
    Works locally or on Vercel without code changes.
    """

    # Initialize Flask app
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )

    register_error_handlers(app)

    # Load configuration from environment variables with defaults
    app.config.from_object(Config)

    # Initialize Redis attached to app instance
    init_redis(app)

    # Register blueprints
    from app.routes.view_routes import view_bp
    from app.routes.api_spin_routes import spin_bp
    from app.routes.api_guess_routes import guess_bp
    from app.routes.api_media_routes import media_bp
    from app.routes.api_test_routes import test_bp

    app.register_blueprint(view_bp)
    app.register_blueprint(spin_bp)
    app.register_blueprint(guess_bp)
    app.register_blueprint(media_bp)
    app.register_blueprint(test_bp)

    return app
