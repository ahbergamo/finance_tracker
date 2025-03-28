import os
from dotenv import load_dotenv
from app import create_app

# Load environment variables from .env
load_dotenv()

# Default to DevelopmentConfig if FLASK_CONFIG is not set
config_object = os.environ.get("FLASK_CONFIG", "config.config.DevelopmentConfig")

# Create the Flask app with the selected config
app = create_app()

if __name__ == "__main__":
    # Read DEBUG from the actual Flask config
    debug_mode = app.config.get("DEBUG", True)  # Default to True if not explicitly set

    app.run(host="0.0.0.0", port=5002, debug=debug_mode)
