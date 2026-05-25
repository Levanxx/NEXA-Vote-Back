import os
from flask import Flask
from flask_cors import CORS

from app.routes.registration import registration_bp
from app.routes.biometric import biometric_bp
from app.routes.webauthn import webauthn_bp
from app.routes.auth import auth_bp
from app.routes.mfa import mfa_bp
from app.routes.candidates import candidates_bp
from app.routes.votes import votes_bp
from app.routes.admin import admin_bp


def create_app():
    app = Flask(__name__)

    allowed_origins = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:5173"
    ).split(",")

    CORS(app, origins=allowed_origins)

    app.register_blueprint(registration_bp)
    app.register_blueprint(biometric_bp)
    app.register_blueprint(webauthn_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mfa_bp)
    app.register_blueprint(candidates_bp)
    app.register_blueprint(votes_bp)
    app.register_blueprint(admin_bp)

    return app