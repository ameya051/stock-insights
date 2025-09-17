import os
from app import create_app


app = create_app()


if __name__ == "__main__":
    # Configurable local run: default to non-debug and respect PORT.
    port = int(os.getenv("PORT", "5000"))
    debug_env = os.getenv("FLASK_DEBUG", "0").lower()
    debug = debug_env in {"1", "true", "yes", "on"}
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=debug)
