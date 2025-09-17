from flask import Flask
from dotenv import load_dotenv


def create_app() -> Flask:
    """Application factory for the Flask app."""
    # Load environment variables from a .env file if present
    load_dotenv()
    app = Flask(__name__)

    # Register blueprints
    from .routes.ping import ping_bp
    app.register_blueprint(ping_bp, url_prefix='/api')

    # FMP data endpoints
    try:
        from .routes.fetch_data import fmp_bp
        app.register_blueprint(fmp_bp, url_prefix='/api')
    except Exception:
        # If route import fails during certain tooling, skip to avoid crashing app creation
        pass

    # Recommendations endpoints
    try:
        from .routes.recommendations import recs_bp
        app.register_blueprint(recs_bp, url_prefix='/api')
    except Exception:
        pass

    return app
