from flask import Flask
from flask_cors import CORS
import logging

def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
    app.secret_key = 'your_secret_key'  # Replace with a secure key

    logging.basicConfig(level=logging.DEBUG)

    # Register blueprints
    from .routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
