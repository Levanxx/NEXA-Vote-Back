from flask import Flask
from flask_cors import CORS

from app.routes.registration import registration_bp
from app.routes.biometric import biometric_bp
from app.routes.webauthn import webauthn_bp
from app.routes.auth import auth_bp
from app.routes.mfa import mfa_bp


def create_app():

    app = Flask(__name__)

    CORS(app, origins=["http://localhost:5173"])


    app.register_blueprint(registration_bp)
    app.register_blueprint(biometric_bp)
    app.register_blueprint(webauthn_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mfa_bp)


    return app