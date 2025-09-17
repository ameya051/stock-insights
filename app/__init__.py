from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv


def create_app() -> Flask:
    """Application factory for the Flask app."""
    # Load environment variables from a .env file if present
    load_dotenv()
    app = Flask(__name__)
    # Enable CORS for API routes; adjust origins via CORS_ORIGINS env if needed
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        expose_headers=["Content-Type"],
        max_age=600,
    )

    # Register all blueprints found under app.routes automatically
    from .routes import register_blueprints
    register_blueprints(app, package="app.routes", url_prefix="/api")

    return app
