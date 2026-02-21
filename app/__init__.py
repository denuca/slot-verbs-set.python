import os
from flask import Flask
from app.extensions import init_redis

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

    # Load configuration from environment variables with defaults
    app.config["DEFAULT_SLOT_COUNT"] = int(os.getenv("DEFAULT_SLOT_COUNT", 3))
    app.config["MAX_SLOT_COUNT"] = int(os.getenv("MAX_SLOT_COUNT", 5))
    app.config["REDIS_URL"] = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    app.config["FLASK_ENV"] = os.getenv("FLASK_ENV", "development")
    app.config["MAX_ATTEMPTS"] = os.getenv("MAX_ATTEMPTS", "999")
    app.secret_key = os.getenv("SECRET_KEY", "dev_key")

    # Initialize Redis attached to app instance
    init_redis(app)

    # Register blueprints
    from app.routes.view_routes import view_bp
    from app.routes.api_spin_routes import spin_bp
    from app.routes.api_guess_routes import guess_bp
    from app.routes.api_test_routes import test_bp

    app.register_blueprint(view_bp)
    app.register_blueprint(spin_bp)
    app.register_blueprint(guess_bp)
    app.register_blueprint(test_bp)

    return app
