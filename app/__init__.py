from flask import Flask
from flask_cors import *
from app.config import Config


def create_app():
    app = Flask(__name__, template_folder='.')
    CORS(app, supports_credentials=True)
    app.config.from_object(Config)
    Config.init_app(app)
    return app
