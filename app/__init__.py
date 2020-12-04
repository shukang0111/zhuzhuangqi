from flask import Flask, Response
from werkzeug.datastructures import Headers
from flask_cors import *
from app.config import Config


def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True)
    app.config.from_object(Config)
    Config.init_app(app)
    return app
