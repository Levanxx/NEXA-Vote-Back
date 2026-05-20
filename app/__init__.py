from flask import Flask
from app.routes.registration import registration_bp
from flask_cors import CORS

def create_app():

    app = Flask(__name__)

    CORS(app, origins=[
        "http://localhost:5173"
    ])

    app.register_blueprint(registration_bp)

    return app